# Stack Compiler Interchange Specification

## Status

This document is a normative part of the draft Stack 1.0 specification. It defines portable JSON representations for normalized compiler output, diagnostics, and canonical conformance expectations.

The JSON Schemas in [`schemas/`](./schemas) are normative for document shape. This document is normative for field meaning, ordering, and processing behavior.

## 1. Scope

The compiler interchange boundary follows language processing stages 1 through 4:

```text
UTF-8 source
    -> tokenization and parsing
    -> identifier and default resolution
    -> semantic and complexity validation
    -> normalized diagram IR
```

Theme and icon resolution, layout solving, and rendering occur after this boundary. They MUST NOT add fields to normalized compiler IR.

A native compiler API MAY expose implementation-specific types. An implementation claiming portable conformance MUST be able to map its successful output and diagnostics to the JSON contracts defined here.

## 2. Interchange Version

Every interchange document contains `schemaVersion`. Stack 1.0 defines schema version `1.0`.

The schema version is independent of the Stack language version:

- `languageVersion` identifies the source grammar and semantics;
- `schemaVersion` identifies the portable JSON representation.

Adding an optional field is a schema minor change. Removing a field, changing a field meaning, changing an enum meaning, or making an optional field required is a schema major change.

Consumers MUST reject unsupported schema major versions. They MUST NOT silently ignore unknown fields because an unknown field may carry required meaning.

## 3. Normalized Diagram IR

A compiler produces normalized IR only when stages 1 through 4 contain no error diagnostics. Warning diagnostics may accompany successful IR.

The normalized document conforms to [`normalized-ir.schema.json`](./schemas/normalized-ir.schema.json).

### 3.1 Normalization Rules

Normalized IR MUST:

- include the declared language version;
- apply `default` when no theme is authored;
- apply `service` when no node kind is authored;
- apply `flow` when no edge kind is authored;
- preserve node, group, edge, child, same-rank, and order list declaration order;
- represent absent optional values as JSON `null`;
- represent collections as arrays, including when empty;
- use source identifiers without case conversion;
- contain decoded string values rather than source escapes.

Normalized IR MUST NOT contain:

- source locations, comments, or formatting trivia;
- unresolved or partial declarations from invalid source;
- theme or icon catalog resolution results;
- coordinates, dimensions, edge paths, colors, typography, or SVG;
- implementation-specific filesystem, network, memory, or object handles.

JSON object member order has no meaning. Array order is normative.

### 3.2 Diagram Fields

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Compiler interchange version; `1.0` for this document |
| `languageVersion` | Major and minor version declared by the source |
| `title` | Decoded visible diagram title |
| `themeId` | Authored theme identifier or `default` |
| `children` | Direct diagram children in declaration order |
| `nodes` | Every node in depth-first declaration order |
| `groups` | Every group in depth-first declaration order |
| `edges` | Diagram edges in declaration order |
| `layout` | Normalized diagram layout or `null` |

Each child reference contains `type` and `id`. The type is `node` or `group`. Although Stack identifiers are globally unique, the explicit type prevents consumers from inferring element category from another array.

### 3.3 Nodes and Groups

A node contains its effective semantic kind and nearest containing group. `parentGroupId` is `null` for a root node. `iconId` and `detail` remain `null` when omitted; icon fallback and visual detail treatment are downstream concerns.

A group contains its nearest containing group, direct children, and group-scoped layout. `parentGroupId` is `null` for a root group. Group entries use depth-first declaration order: a parent precedes all descendants.

Containment is intentionally represented in both directions:

- `children` supports ordered traversal of one scope;
- `parentGroupId` supports direct lookup from a node or group.

Both representations MUST agree.

### 3.4 Edges

`from` and `to` preserve the authored left and right endpoint order. `direction` is one of:

- `forward` for `->`;
- `bidirectional` for `<->`;
- `association` for `--`.

Bidirectional and association edges preserve authored endpoint order even though duplicate-edge validation treats their endpoint order as equivalent.

### 3.5 Layout

Layout contains:

- `direction`: `right`, `down`, or `null`;
- `sameRanks`: same-rank identifier lists in declaration order;
- `order`: the authored order list or `null`.

The identifiers remain scoped to the direct children of the diagram or group that owns the layout. Normalized IR does not contract edges or solve positions.

## 4. Diagnostic Interchange

A portable diagnostic conforms to [`diagnostic.schema.json`](./schemas/diagnostic.schema.json).

### 4.1 Positions and Ranges

A position contains:

- `byteOffset`: zero-based UTF-8 byte offset in the original source;
- `line`: one-based line number;
- `column`: one-based Unicode scalar column.

A range contains an inclusive `start` position and an exclusive `end` position. A point diagnostic has identical start and end positions. LF and CRLF each advance the line once; byte offsets still count their original encoded bytes.

### 4.2 Fields

`code` and its normative meaning are assigned by the language specification. `severity` is `error` or `warning`. `message` is concise human-readable text but its exact wording is not a compatibility guarantee.

`expected` is always an array of unique, non-empty strings. It contains source values or grammatical constructs that are valid at the primary range and is empty when no useful candidate exists. It provides correction context, not a replacement edit or a completion contract.

Closed sets contain every valid value in specification order. Syntax diagnostics use exact source spellings for literal tokens and angle-bracket names such as `<identifier>` or `<string>` for token classes. Identifier suggestions contain at most three visible identifiers. Suggestions are eligible when their Unicode-scalar Levenshtein distance is no greater than one third of the longer identifier length, rounded down, with a minimum threshold of one. They are ordered by ascending distance and then by bytewise identifier order.

`help` is either corrective guidance or `null`. `related` is always an array and identifies other source ranges involved in the diagnostic. When an identifier suggestion names an existing declaration, related information SHOULD identify that declaration. Related-information message wording is not a compatibility guarantee.

Implementations may emit non-`STK` diagnostics. Canonical fixtures only require portable `STK` diagnostics unless a case explicitly documents an implementation extension.

## 5. Canonical Compiler Conformance Suite

The canonical compiler suite lives in `conformance/valid/` and `conformance/invalid/`. Each compiler case is one directory named with a lowercase ASCII identifier. Formatter fixtures use a separate contract and layout defined in the [Stack Canonical Formatter Specification](./FORMATTER.md).

### 5.1 Valid Cases

A valid case contains:

```text
conformance/valid/<case-id>/source.stack
conformance/valid/<case-id>/expected.ir.json
conformance/valid/<case-id>/expected.diagnostics.json  # optional
```

The source MUST compile to normalized IR semantically equal to `expected.ir.json`. If `expected.diagnostics.json` is absent, no portable diagnostics are expected. When present, it normally contains warning expectations.

### 5.2 Invalid Cases

An invalid case contains:

```text
conformance/invalid/<case-id>/source.stack
conformance/invalid/<case-id>/expected.diagnostics.json
```

The source MUST NOT produce normalized IR. Its portable diagnostics MUST match the expectation document.

### 5.3 Diagnostic Expectations

Expectation documents conform to [`diagnostic-expectations.schema.json`](./schemas/diagnostic-expectations.schema.json). Each expected diagnostic requires code, severity, and range. A fixture may also include `expected` when its exact values and ordering are part of the case.

Runners compare diagnostics in the deterministic order emitted by the compiler. They MUST compare the number of diagnostics and MUST NOT ignore additional portable diagnostics. When a fixture includes `expected`, runners compare that array exactly. They do not compare message, help, or related information.

### 5.4 Runner Behavior

A conforming runner MUST:

1. discover case directories in bytewise identifier order;
2. read `source.stack` as bytes so encoding fixtures remain possible;
3. compile with catalog, layout, and renderer stages disabled;
4. validate successful normalized output against the normalized IR schema;
5. validate expectation documents against their schemas;
6. compare JSON values semantically rather than by object-member order or whitespace;
7. fail a case when required files are missing or unexpected files use reserved names;
8. report the case identifier and mismatch location.

An implementation MUST record the specification release or commit revision used for its conformance run. Passing an older suite does not claim support for a newer specification revision.
