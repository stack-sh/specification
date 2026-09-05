# Stack Language Intelligence Specification

## Status

This document is a normative part of the draft Stack 1.0 specification. It defines the protocol-neutral operations and portable data shared by native tools, WebAssembly adapters, language servers, browser editors, command-line tools, and agents.

The JSON Schema in [`schemas/language-intelligence.schema.json`](./schemas/language-intelligence.schema.json) is normative for request and response shape. This document is normative for field meaning, ordering, recovery, and ownership.

## 1. Scope

Stack language intelligence covers these source-oriented operations:

- compiler diagnostics;
- completion;
- hover;
- document symbols;
- canonical-format text edits.

The contract is not a transport protocol. It does not define JSON-RPC, process lifecycle, document storage, filesystem access, network access, cancellation messages, or editor UI. In particular, it does not copy the Language Server Protocol data model. An LSP adapter maps this contract to the capabilities negotiated with its client.

Theme resolution, provider-pack loading, layout, rendering, and artifact paths remain outside the compiler boundary. A caller may supply already validated icon identifiers as completion catalog data, but language intelligence MUST NOT fetch a catalog or interpret catalog text as instructions.

## 2. Contract Version and Envelopes

Every request and response contains `schemaVersion`. Stack 1.0 defines language-intelligence schema version `1.0`.

Every operation also contains:

- `kind`: `request` or `response`;
- `documentVersion`: a non-negative caller-owned snapshot version;
- `feature`: `diagnostics`, `completion`, `hover`, `documentSymbols`, or `format`.

A response MUST echo the request's `schemaVersion`, `documentVersion`, and `feature`. Consumers MUST discard a response when its document version is no longer current. Implementations MUST reject unsupported schema major versions and MUST NOT silently ignore unknown fields.

Adding an optional field is a schema minor change. Removing a field, changing a field meaning or enum meaning, or making an optional field required is a schema major change.

## 3. Source Positions and Ranges

Language intelligence reuses the source position and range contract from the [compiler interchange specification](./INTERCHANGE.md#41-positions-and-ranges):

- `byteOffset` is a zero-based UTF-8 byte offset in the complete source snapshot;
- `line` is one-based;
- `column` is a one-based Unicode scalar column;
- range start is inclusive and range end is exclusive.

A request position MUST identify a UTF-8 scalar boundary and its three coordinates MUST agree. A position at the end of the source is valid. A response range MUST belong to the exact source snapshot identified by `documentVersion`.

Protocol adapters own coordinate conversion. For example, an LSP adapter converts between this contract and the position encoding negotiated with the client. The compiler MUST NOT expose LSP-specific zero-based or UTF-16 coordinates.

## 4. Diagnostics

Every response contains `diagnostics`, even when empty. Each entry conforms to [`diagnostic.schema.json`](./schemas/diagnostic.schema.json) and retains the diagnostic ordering defined by the compiler interchange specification.

The compiler returns every portable diagnostic available for the snapshot. Syntax recovery may limit that set; Stack 1.0 does not require a partial syntax tree or multiple syntax errors. Human-readable message, help, hover prose, and related-information wording are not compatibility guarantees. Code, severity, source range, and any fixture-pinned `expected` values are portable meaning.

An operation MAY return useful completion data alongside error diagnostics. Hover and document symbols MAY be empty when the implementation cannot recover a trustworthy construct. Formatting MUST return no edits after an encoding, lexical, or syntax error; a syntactically valid document with semantic errors MAY still be formatted.

## 5. Completion

A completion request contains a position and an explicit `completionCatalog`. The catalog contains zero or more caller-owned icon entries. An entry contains its exact Stack icon identifier, a display label, and optional plain-text detail and documentation. Implementations MUST bound catalog size and text length before processing untrusted input.

A completion response contains `isIncomplete` and `items`:

- `isIncomplete` is `true` when additional typing or a more complete snapshot may produce a materially different list;
- `items` are ordered by ascending `sortText`, then bytewise `label`;
- duplicate pairs of `label` and `edit` are not allowed.

Each item has one semantic kind:

- `keyword`: a grammatical Stack keyword;
- `property`: a property or layout statement valid in the current block;
- `enumValue`: a closed value from the language specification;
- `identifier`: a document-local node or group identifier valid at the position;
- `icon`: an identifier supplied through the completion catalog.

`filterText` is the plain string a consumer filters against. `detail` and `documentation` are plain text or `null`; they MUST NOT contain Markdown, HTML, commands, or executable links. The required `edit` replaces the complete source token or incomplete token fragment relevant to the item. Its range contains the request position and its `newText` is literal Stack source, not a snippet.

Closed language values use specification order. Document identifiers use declaration order. Catalog icons use bytewise identifier order. An implementation MAY omit candidates it cannot establish safely, but MUST NOT invent syntax, enum values, identifiers, or icon IDs.

For an icon item, `label` is the catalog entry's display label, `filterText`, `sortText`, and edit text use its exact `id`, and optional detail and documentation are copied without interpretation.

Completion SHOULD remain available from a recognizable lexical context when the complete document does not parse. Such a response sets `isIncomplete` when recovery cannot establish the enclosing construct unambiguously.

## 6. Hover

A hover response contains `hover`, either `null` or an object with:

- the exact source range being described;
- a semantic kind: `diagram`, `group`, `node`, `edge`, or `property`;
- a short label;
- optional plain-text detail and documentation.

Hover text is presentation-neutral plain text. It MUST NOT contain raw HTML, executable commands, or fetched content. A reference hover describes the declaration resolved by compiler semantics while retaining the range of the reference under the request position.

When multiple constructs cover a position, the smallest trustworthy construct wins. An implementation returns `null` instead of guessing when parsing or name resolution cannot identify one construct.

## 7. Document Symbols

A document-symbol response contains `symbols` in source order. Each symbol has:

- `name`: the user-visible label or a concise edge description;
- `kind`: `diagram`, `group`, `node`, or `edge`;
- `detail`: stable plain-text secondary information or `null`;
- `range`: the complete declaration;
- `selectionRange`: the most useful authored token within that declaration;
- `children`: directly nested symbols in source order.

`selectionRange` MUST be contained by `range`. A child range MUST be contained by its parent range. The diagram is the root symbol; groups contain their direct node and group declarations; diagram-scope edges are children of the diagram. Symbol output reflects syntax structure and MAY be returned for a syntactically valid document with semantic errors.

## 8. Format Edits

A format response contains `edits`. Each edit has an end-exclusive range in the input snapshot and literal `newText`.

Edits MUST be ordered by ascending range start and MUST NOT overlap. All ranges are interpreted against the unchanged input snapshot; consumers apply multiple edits from the end of the document toward the beginning. Stack's canonical formatter SHOULD return either:

- an empty array when the source is already canonical; or
- one whole-document edit when canonical output differs.

The formatter owns canonical source generation. The compiler owns the shared `TextEdit` representation but MUST NOT duplicate formatter behavior.

## 9. Snapshot and Incremental Boundaries

The compiler core is stateless. Every operation evaluates one complete, caller-owned UTF-8 snapshot. It does not retain document text, apply deltas, schedule work, or decide whether a result is stale.

A stateful adapter MAY accept incremental changes. Before calling the compiler it MUST:

1. validate that the change applies to the expected document version;
2. convert protocol positions to valid UTF-8 byte boundaries;
3. apply the change to its private snapshot;
4. invoke the compiler with the complete updated source;
5. echo the updated version in the portable response;
6. suppress a cancelled or stale result before publication.

This boundary lets native and WebAssembly consumers share deterministic compiler semantics without forcing one document store or transport into the compiler crate.

## 10. Ownership

| Owner | Responsibility |
| --- | --- |
| `stack-sh/specification` | Normative prose, JSON Schemas, canonical fixtures, language values, portable compatibility |
| `stack-sh/compiler` | Stateless diagnostics, semantic completion, hover resolution, document symbols, source ranges, dependency-free native types |
| `stack-sh/engine` formatter | Canonical formatting and conversion of changed output to portable text edits |
| WebAssembly adapter | Validated JSON / JavaScript boundary, document-version echo, catalog input bounds, serialization of compiler-owned results |
| Native LSP adapter | JSON-RPC lifecycle, client capabilities, position-encoding conversion, incremental document store, cancellation, stale-result suppression |
| Editor / CLI / agent consumer | Current document version, edit application, UI presentation, filesystem and process behavior |

The LSP adapter MUST translate rather than redefine diagnostic codes or compiler semantics. WebAssembly and native adapters MUST be able to run the same fixtures under [`conformance/language-intelligence/`](./conformance/language-intelligence).

## 11. Conformance Fixtures

Each case is a lowercase ASCII directory containing exactly:

```text
conformance/language-intelligence/<case-id>/source.stack
conformance/language-intelligence/<case-id>/fixture.json
```

`fixture.json` conforms to [`language-intelligence-fixture.schema.json`](./schemas/language-intelligence-fixture.schema.json). It identifies `source.stack` and contains ordered request / expected-response pairs. A runner MUST:

1. read source as bytes and reject an unsupported encoding before interpreting positions;
2. preserve operation order from the fixture;
3. validate each request and response against the portable schema;
4. invoke the feature with the exact source snapshot, version, position, and catalog;
5. compare the complete semantic JSON value, except prose fields explicitly marked non-normative by a fixture runner;
6. report the case ID, operation ID, and first mismatch;
7. record the exact specification revision used.

The canonical suite includes a valid semantic case, an incomplete syntax case that still returns completion, and a formatting case. Implementations MAY provide more information than a non-exhaustive runtime request normally requires, but canonical fixture responses are exact for claiming conformance to that fixture revision.

## 12. Security and Resource Limits

Source and completion catalogs are untrusted data. Implementations MUST apply the Stack document limits before unbounded analysis and MUST bound catalog entry count and string length. They MUST NOT execute source, render response prose as trusted markup, fetch an icon or URL, access the filesystem, or retain caller data implicitly.

Errors at a host, transport, or serialization boundary are operational failures, not fabricated `STK` diagnostics. Adapters expose such failures through their own typed error channel while preserving the compiler diagnostic contract for source problems.
