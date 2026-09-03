# Stack Language Specification

## Status of This Document

This document is a draft proposal for Stack 1.0. It is the canonical language contract for parser, validator, formatter, and renderer implementations.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

## 1. Language Goals

Stack is a small declarative language for static software architecture and technology-stack diagrams.

Stack has the following goals:

1. **Concise authoring.** A useful diagram should require little more than named nodes and edges.
2. **Reliable generation.** Humans and language models should have one predictable way to express each concept.
3. **Semantic source.** Source describes components, boundaries, and relationships rather than drawing commands.
4. **Polished output.** The language deliberately withholds low-level styling and positioning so a renderer can enforce a coherent visual system.
5. **Stable interchange.** The same valid source should preserve its topology and meaning across conforming implementations.
6. **Useful diagnostics.** Invalid or ambiguous input should produce structured, local, actionable errors.
7. **Safe embedding.** A source file must not execute code, fetch arbitrary assets, or contain renderer-specific escape hatches.
8. **Readable diffs.** Files should remain understandable in source control without generated metadata.

## 2. Non-Goals

Stack 1.0 is not intended to be:

- a general-purpose graph description language;
- a pixel-perfect drawing or page-layout format;
- a replacement for SVG, Canvas, CSS, or design tools;
- a programming language with variables, expressions, macros, imports, or conditionals;
- an executable infrastructure definition or a claim about deployed state;
- a sequence, state-machine, class, entity-relationship, or full UML notation;
- a way to embed arbitrary HTML, Markdown, JavaScript, URLs, or SVG;
- a guarantee of pixel-identical output across renderer versions, fonts, or canvas sizes;
- suitable for an unlimited number of elements in a single diagram.

Large systems should be explained as multiple focused Stack diagrams rather than one exhaustive graph.

## 3. Core Concepts and Terminology

### 3.1 Document

A **document** is one UTF-8 `.stack` file. It contains one language version directive and exactly one diagram.

### 3.2 Diagram

A **diagram** is the root semantic and layout scope. It has a human-readable title and contains an optional theme selection, nodes, groups, edges, and at most one layout block.

### 3.3 Node

A **node** is an addressable architectural entity, such as a user, client, service, worker, database, queue, or external system. Every node has a globally unique identifier and a visible label.

### 3.4 Group

A **group** is a labeled containment boundary. It communicates that its descendant nodes belong to the same system, domain, network boundary, deployment area, team boundary, or another author-defined concern.

A group does not imply runtime isolation, security, ownership, or deployment semantics beyond the containment visible in the diagram. Authors communicate the particular meaning through the group label.

### 3.5 Edge

An **edge** is a relationship between two nodes. Its operator states directionality, while its optional kind and label state the nature of the relationship.

Groups cannot be edge endpoints in Stack 1.0. Authors must connect the specific boundary node, gateway, service, or other component that participates in the relationship.

### 3.6 Identifier

An **identifier** is a source-level name used for references. Identifiers are case-sensitive, are never displayed, and share one global namespace across nodes and groups.

### 3.7 Label and Detail

A **label** is the primary visible name of a diagram element or edge. A node **detail** is an optional secondary line for a technology, responsibility, or other short qualifier.

Labels and details are plain text. They do not support Markdown or HTML.

### 3.8 Theme

A **theme** is a symbolic reference to a renderer-managed visual system. It may control palette, typography, surfaces, icons, connectors, and background treatment without changing diagram meaning.

### 3.9 Constraint and Hint

A **constraint** is a layout requirement that a renderer must satisfy. A **hint** expresses author intent that a renderer should follow when compatible with stronger constraints and output quality.

Stack exposes very few of either. It never exposes coordinates.

## 4. Lexical Structure

### 4.1 Encoding and File Extension

Documents MUST be UTF-8. The conventional file extension is `.stack`.

A byte order mark is not permitted. Line endings may be LF or CRLF and have identical meaning.

### 4.2 Whitespace

Spaces, tabs, and line endings separate tokens and are otherwise insignificant. Indentation is recommended for readability but has no semantic meaning.

### 4.3 Comments

A line comment starts with `//` and continues to the end of the line. Comments are permitted anywhere whitespace is permitted.

Block comments are not supported.

### 4.4 Identifiers

Identifiers match:

```text
[a-z][a-z0-9_-]*
```

Identifiers contain between 1 and 64 ASCII characters. Keywords are recognized contextually. A word that matches a keyword may also be used where the grammar expects an identifier, although authors SHOULD avoid identifiers that make a declaration difficult to read. The lowercase ASCII form avoids quoting, normalization, and visually confusable references.

### 4.5 Strings

Strings are enclosed in double quotes. Source text may contain Unicode directly.

The only escapes are:

| Escape | Meaning |
| --- | --- |
| `\"` | Double quote |
| `\\` | Backslash |
| `\uXXXX` | Unicode code unit |

Decoded strings MUST NOT contain line breaks, tabs, control characters, or unpaired surrogates. A title, label, or detail MUST NOT begin or end with a Unicode whitespace character. Length limits count decoded Unicode scalar values.

Renderers MUST treat strings as plain text and MUST NOT interpret Markdown or HTML syntax within them.

### 4.6 Icon Identifiers

An icon identifier is written as a string with this logical form:

```text
icon-name
```

The decoded identifier matches `[a-z0-9][a-z0-9-]*` and contains between 1 and 64 ASCII characters. Icon identifiers are case-sensitive and are resolved within the diagram's effective theme.

## 5. Grammar

The grammar below uses ISO-style EBNF. `identifier`, `string`, and `integer` are lexical tokens. Whitespace and comments are omitted.

```ebnf
document          = version-directive, diagram-declaration, EOF ;

version-directive = "stack", integer, ".", integer ;

diagram-declaration
                  = "diagram", string, "{", { diagram-member }, "}" ;

diagram-member    = node-declaration
                  | group-declaration
                  | edge-declaration
                  | theme-statement
                  | layout-block ;

theme-statement   = "theme", identifier ;

group-declaration = "group", identifier, string, "{", { group-member }, "}" ;

group-member      = node-declaration
                  | group-declaration
                  | layout-block ;

node-declaration  = "node", identifier, string, [ node-block ] ;

node-block        = "{", node-property, { node-property }, "}" ;

node-property     = "kind", node-kind
                  | "icon", string
                  | "detail", string ;

node-kind         = "actor"
                  | "client"
                  | "service"
                  | "function"
                  | "worker"
                  | "database"
                  | "cache"
                  | "queue"
                  | "storage"
                  | "external" ;

edge-declaration  = "edge", identifier, edge-operator, identifier,
                    [ string ], [ edge-block ] ;

edge-operator     = "->" | "<->" | "--" ;

edge-block        = "{", edge-property, { edge-property }, "}" ;

edge-property     = "kind", edge-kind ;

edge-kind         = "flow"
                  | "request"
                  | "event"
                  | "data"
                  | "dependency" ;

layout-block      = "layout", "{", layout-statement,
                    { layout-statement }, "}" ;

layout-statement  = direction-statement
                  | rank-statement
                  | order-statement ;

direction-statement
                  = "direction", ( "right" | "down" ) ;

rank-statement    = "rank", "same", identifier-list ;

order-statement   = "order", identifier-list ;

identifier-list   = "[", identifier, ",", identifier,
                    { ",", identifier }, "]" ;

integer           = "0" | nonzero-digit, { digit } ;
nonzero-digit     = "1" | "2" | "3" | "4" | "5"
                  | "6" | "7" | "8" | "9" ;
digit             = "0" | nonzero-digit ;
```

### 5.1 Contextual Keywords

The following words have grammatical meaning in Stack 1.0:

```text
stack diagram group node edge theme layout kind icon detail direction
rank same order right down actor client service function worker
database cache queue storage external flow request event data dependency
```

They remain valid identifiers where the grammar expects an identifier. This contextual treatment allows future minor versions to add keywords without invalidating existing identifiers.

### 5.2 Canonical Formatting

Formatting does not affect meaning. The normative canonical source representation, including comment placement, ordering, whitespace, string escaping, line endings, and conformance requirements, is defined in the [Stack Canonical Formatter Specification](./FORMATTER.md).

A canonical formatter MUST preserve normalized meaning and comments, and formatting canonical source again MUST produce byte-identical output.

## 6. Document and Diagram Semantics

The version directive MUST be the first non-comment token. A document MUST contain exactly one diagram and no trailing declarations.

The diagram title is required and MUST contain between 1 and 80 Unicode scalar values. A diagram MUST contain at least one node.

The order of node, group, and edge declarations does not define visual placement. Edges may reference nodes declared later in the document.

### 6.1 Theme Selection

A diagram may contain at most one theme statement:

```stack
diagram "Service architecture" {
  theme dark

  node api "API"
}
```

If the statement is omitted, the effective theme is `default`.

`@stack-sh/theme` is the canonical, versioned, open source catalog for Stack themes and their icons. A renderer resolves the requested theme from the installed catalog version and SHOULD record that version in output metadata. Stack source selects a theme identifier but does not pin a catalog package version.

Stack 1.0 requires the catalog to provide these theme identifiers:

| Theme | Required behavior |
| --- | --- |
| `default` | The renderer's standard polished visual system |
| `light` | A visual system intended for a light background |
| `dark` | A visual system intended for a dark background |

Failure to provide a required theme is a catalog or renderer implementation failure, not a source warning.

Theme identifiers use the normal Stack identifier syntax and have no namespace. The first catalog pull request merged for an identifier registers it. A registered identifier MUST NOT be assigned to a different theme later, even if its original theme is deprecated or removed. This first-merged rule makes theme selection globally unambiguous without adding package or contributor names to source.

A requested theme that is not present in the installed catalog version produces warning `STK6001` and falls back to `default`, so the topology remains renderable.

A theme may affect typography metrics and therefore exact element positions, but it MUST NOT change or hide nodes, groups, edges, labels, directionality, semantic kinds, or layout constraints. Every theme MUST preserve legibility, accessible contrast, and non-color distinctions required elsewhere in this specification.

Each theme owns its icon collection. This is a one-to-many relationship: one selected theme resolves zero or more authored icon identifiers to theme-specific SVG assets. The same logical icon may therefore use different SVG artwork in `light`, `dark`, or any other theme.

Stack source cannot define theme values, inherit from a network resource, or add per-element visual overrides. The catalog is explicitly installed or bundled by the renderer and MUST NOT be fetched solely because a theme identifier appears in source.

## 7. Node Semantics

### 7.1 Identity and Labels

A node identifier MUST be unique among every node and group in the document. A node label MUST contain between 1 and 60 Unicode scalar values.

Two nodes may have the same visible label when they represent distinct entities, though authors SHOULD prefer labels that remain understandable without relying on position.

### 7.2 Kinds

`kind` provides coarse architectural meaning and selects a theme-controlled visual treatment and fallback.

| Kind | Intended meaning |
| --- | --- |
| `actor` | A person, role, team, or autonomous participant |
| `client` | A browser, mobile app, desktop app, device, or other client |
| `service` | A long-running application, API, gateway, or general software component |
| `function` | An on-demand or serverless compute unit |
| `worker` | A background processor or scheduled job |
| `database` | A durable queryable datastore |
| `cache` | A datastore whose contents are disposable or derived |
| `queue` | A queue, stream, bus, or broker used for asynchronous delivery |
| `storage` | Blob, object, file, or archival storage |
| `external` | A system outside the architecture's control boundary |

The default kind is `service`.

A node block MUST NOT contain the same property more than once. Kinds are semantic categories, not vendor-specific shapes. For example, a hosted PostgreSQL instance remains `database`.

### 7.3 Detail

`detail` supplies a visible secondary line. It MUST contain between 1 and 80 Unicode scalar values. It SHOULD name one technology or one short responsibility, not a paragraph.

When authored, `detail` MUST remain visible in every rendered diagram. A renderer or theme MUST NOT omit it, reduce it to tooltip-only content, or expose it only through accessibility metadata.

Examples include `"Next.js"`, `"Order orchestration"`, and `"PostgreSQL 17"`.

### 7.4 Icons

`icon` decorates a node without changing its kind, identity, or accessibility label. It names a logical icon in the diagram's effective theme:

```stack
node database "Primary database" {
  kind database
  icon "postgresql"
}
```

Every theme in `@stack-sh/theme` MUST provide a fallback visual treatment for every node kind. Named icons beyond those fallbacks are theme-owned. The same icon identifier used by multiple themes MUST represent the same logical subject, but each theme MAY provide different SVG artwork appropriate to its palette and visual system.

If `icon` is omitted, the renderer uses the selected theme's fallback for the node kind. If an authored icon identifier is absent from the selected theme, rendering continues with that fallback and emits warning `STK5001`.

Renderers MUST NOT fetch an icon from an arbitrary network location solely because it appears in source. Icon assets, licensing, validation, caching, and updates are concerns of `@stack-sh/theme`. Renderers SHOULD report the resolved icon identifier and catalog version in output metadata so visual changes can be reproduced.

Icons MUST NOT be the only accessible indication of a node's meaning. Renderers control icon size, color, stroke, masking, and placement to preserve visual consistency.

## 8. Group Semantics

A group is a visual containment boundary with a globally unique identifier and a label of 1 to 60 Unicode scalar values.

A group may contain nodes and nested groups. It may also contain one layout block. It may not contain edges; all edges are declared at diagram scope.

The following rules apply:

- Every group MUST contain at least one descendant node.
- Group nesting MUST NOT exceed three levels below the diagram.
- A node belongs to its nearest enclosing group and, transitively, to all ancestor groups.
- A node cannot appear in more than one group because declarations cannot be reused.
- A group identifier cannot be used as an edge endpoint.
- A group does not create an implicit node or implicit edges.

Renderers MUST draw containment unambiguously. They MAY vary group border, fill, label placement, and padding, but MUST NOT imply a group kind that does not exist in source.

## 9. Edge Semantics

### 9.1 Endpoints and Direction

Edge endpoints MUST resolve to two distinct nodes. Forward references are valid. Self-edges are invalid in Stack 1.0.

| Operator | Meaning |
| --- | --- |
| `->` | A directed relationship from the left node to the right node |
| `<->` | One symmetric relationship in both directions |
| `--` | An association for which direction is absent or intentionally unspecified |

`<->` is one relationship, not shorthand for two independently labeled edges.

### 9.2 Kinds

The optional edge kind describes the relationship independently of its protocol label.

| Kind | Intended meaning |
| --- | --- |
| `flow` | A generic runtime or conceptual flow; the default |
| `request` | A synchronous request or call |
| `event` | Asynchronous message or event delivery |
| `data` | Data movement, replication, reads, or writes |
| `dependency` | A build-time, deployment-time, or operational dependency |

The default kind is `flow`. Renderers MUST distinguish directionality and SHOULD distinguish kinds through a coherent renderer-owned combination of line, dash, weight, and marker treatment. Color alone MUST NOT carry the distinction.

An edge block MUST NOT contain the same property more than once.

### 9.3 Labels and Multiplicity

An edge label is optional and, when present, MUST contain between 1 and 40 Unicode scalar values. It SHOULD name a protocol, event, command, dataset, or purpose, such as `"HTTPS"`, `"OrderPlaced"`, or `"SQL"`.

Multiple edges between the same pair of nodes are valid when they communicate distinct relationships. Exact duplicates with the same endpoints, operator, label, and effective kind after defaults are invalid because they add no meaning and produce ambiguous routing. Endpoint order is ignored when comparing `<->` and `--` edges.

## 10. Layout Constraints and Hints

### 10.1 Renderer-Owned Layout

Stack has no coordinates, dimensions, ports, paths, colors, fonts, line breaks, or z-index. Renderers own those decisions.

A conforming renderer MUST:

- keep node and group boxes from overlapping;
- preserve group containment and nesting;
- keep labels legible and associated with the correct element;
- route edges without passing through node labels or node interiors;
- preserve edge directionality;
- apply consistent spacing and typography within one output;
- fit or expand the canvas rather than clipping semantic content.

A renderer SHOULD minimize edge crossings, bends, excessively long edges, and unnecessary empty space. These are quality goals, not source semantics.

### 10.2 Layout Scope

A diagram or group may contain at most one `layout` block. Group layout statements affect only the group's direct children. Diagram layout statements affect only nodes and groups declared directly in the diagram.

References in `rank` and `order` MUST identify direct children of that layout scope. Each list contains at least two distinct identifiers.

For layout purposes, a scope treats each direct child as one item. An edge between descendants of two different direct children induces a connection between those child items. An edge whose endpoints both belong to one child affects only that child's internal layout. This contraction lets a diagram-level direction meaningfully arrange groups even though groups are not valid edge endpoints.

### 10.3 Direction Hint

`direction right` asks the renderer to prefer left-to-right progression. `direction down` asks it to prefer top-to-bottom progression.

Direction is a strong hint, not a guarantee that every edge points in that geometric direction. A diagram without a direction uses renderer-selected automatic layout. Nested groups do not inherit direction unless a renderer's automatic layout independently chooses it.

Each layout block may contain at most one direction statement.

### 10.4 Same-Rank Constraint

`rank same [a, b, c]` requires the listed direct children to share one layout rank. For a right-directed scope this normally means vertical alignment; for a down-directed scope it normally means horizontal alignment.

A child MUST NOT occur in more than one same-rank statement in the same scope. Renderers MUST satisfy valid same-rank constraints.

### 10.5 Order Hint

`order [a, b, c]` gives a preferred relative order for the listed direct children. In a right-directed scope it is interpreted top-to-bottom; in a down-directed scope it is interpreted left-to-right. In automatic layout it is interpreted along the renderer's chosen cross-axis.

The list may omit other children. An omitted child has no author-specified position relative to the list. Each layout block may contain at most one order statement.

Order is a hint. A renderer may deviate from it to satisfy containment, same-rank constraints, legibility, or output bounds. When it does, it SHOULD emit warning `STK4001` in diagnostic-capable environments.

### 10.6 Complexity Limits

The following limits are part of Stack 1.0 validity and exist to preserve readable output:

| Item | Limit |
| --- | ---: |
| Diagrams per document | 1 |
| Nodes | 1 to 40 |
| Groups | 0 to 12 |
| Group nesting below diagram | 3 |
| Edges | 0 to the smaller of 80 or twice the node count |
| Node degree before a warning | 12 |

A document that exceeds a hard limit is invalid. A renderer SHOULD suggest splitting it into focused diagrams. A node with more than 12 incident edge declarations is valid but produces warning `STK4002` because dense hubs often reduce legibility; each edge declaration counts once regardless of directionality.

These limits constrain source complexity, not image resolution. Implementations may enforce lower operational limits only when they clearly report that they are implementation limits rather than language errors.

## 11. Validation and Error Handling

### 11.1 Processing Stages

Implementations SHOULD process a document in these stages:

1. Decode UTF-8 and tokenize.
2. Parse the declared grammar.
3. Resolve identifiers and defaults.
4. Validate semantic and complexity rules.
5. Resolve the selected theme and its icons from `@stack-sh/theme`.
6. Solve layout constraints and apply hints using the effective theme's metrics.
7. Render.

Errors in stages 1 through 4 prevent rendering. Theme or icon catalog warnings and layout-hint warnings do not prevent rendering.

### 11.2 Diagnostics

Every diagnostic MUST include:

- a stable code;
- severity: `error` or `warning`;
- a concise message;
- a one-based source range with start and end line and column;
- an ordered list of expected source values or constructs, which is empty when no useful candidate exists.

A diagnostic SHOULD also include a corrective hint and related source ranges when another declaration caused the problem.

Diagnostic codes use these families:

| Range | Category |
| --- | --- |
| `STK1000`-`STK1999` | Encoding and lexical errors |
| `STK2000`-`STK2999` | Syntax errors |
| `STK3000`-`STK3999` | Name resolution and semantic errors |
| `STK4000`-`STK4999` | Layout and complexity diagnostics |
| `STK5000`-`STK5999` | Icon diagnostics |
| `STK6000`-`STK6999` | Theme diagnostics |
| `STK9000`-`STK9999` | Implementation failures, never source mistakes |

Stack 1.0 assigns the following portable codes:

| Code | Severity | Meaning |
| --- | --- | --- |
| `STK1001` | Error | Input is not valid UTF-8 |
| `STK1002` | Error | A byte order mark is present |
| `STK1003` | Error | A string contains an invalid escape or decoded value |
| `STK2001` | Error | The declared language version is unsupported |
| `STK2002` | Error | An unexpected token, declaration, property, value, or operator was found |
| `STK2003` | Error | Input ended before the current construct was complete |
| `STK3001` | Error | An identifier is invalid |
| `STK3002` | Error | An identifier is declared more than once |
| `STK3003` | Error | An edge references an unknown node |
| `STK3004` | Error | A group is used as an edge endpoint |
| `STK3005` | Error | An edge connects a node to itself |
| `STK3006` | Error | An exact duplicate edge is declared |
| `STK3007` | Error | A property occurs more than once in one block |
| `STK3008` | Error | A title, label, or detail violates its text constraints |
| `STK3009` | Error | A group has no descendant node |
| `STK3010` | Error | Group nesting exceeds the language limit |
| `STK3011` | Error | A layout reference is invalid in its scope |
| `STK3012` | Error | A layout block or singleton layout statement is duplicated |
| `STK3013` | Error | An icon identifier is malformed |
| `STK3014` | Error | A diagram contains more than one theme statement |
| `STK4001` | Warning | An order hint could not be satisfied |
| `STK4002` | Warning | A node exceeds the recommended incident-edge degree |
| `STK4003` | Error | A diagram exceeds a language complexity limit |
| `STK5001` | Warning | An icon identifier is unavailable in the effective theme |
| `STK6001` | Warning | A requested non-core theme is unavailable and `default` was used |

Implementations MAY add diagnostics using their own non-`STK` code prefix. Unassigned `STK` codes are reserved for future specification revisions.

Example diagnostic shape:

```json
{
  "code": "STK3003",
  "severity": "error",
  "message": "Unknown node 'paymnt'.",
  "range": {
    "start": { "byteOffset": 184, "line": 12, "column": 8 },
    "end": { "byteOffset": 190, "line": 12, "column": 14 }
  },
  "expected": ["payment"],
  "help": "Use the declared node 'payment'.",
  "related": [
    {
      "message": "The suggested node is declared here.",
      "range": {
        "start": { "byteOffset": 92, "line": 7, "column": 8 },
        "end": { "byteOffset": 99, "line": 7, "column": 15 }
      }
    }
  ]
}
```

The portable JSON representation is defined by the [Stack Compiler Interchange Specification](./INTERCHANGE.md). Native compiler APIs may expose diagnostics in another representation, but conformance adapters MUST preserve the portable field meanings. Assigned codes and their meanings are normative.

### 11.3 Recovery

A parser MAY recover after an error to report additional independent diagnostics, but MUST NOT render a partial diagram as if the source were valid. Tools that show a live preview MUST make stale or partial output visually distinct from a successful render.

Unknown declarations, properties, enum values, and edge operators are errors. Implementations MUST NOT silently ignore them, because doing so can produce a plausible but semantically incorrect diagram.

### 11.4 Required Semantic Diagnostics

At minimum, validators MUST distinguish:

- unsupported language version;
- invalid or duplicate identifiers;
- missing or invalid labels;
- unknown edge endpoints;
- group identifiers used as edge endpoints;
- self-edges and exact duplicate edges;
- duplicate properties or layout statements;
- duplicate theme statements;
- invalid layout-scope references;
- empty groups and excessive nesting;
- complexity-limit violations;
- malformed icon references;
- unresolved theme-owned icons as warnings;
- unresolved non-core themes as warnings.

Implementations should collect independent semantic errors in one pass rather than stopping after the first error.

### 11.5 Normalized IR and Conformance

A document that completes processing stages 1 through 4 without errors produces normalized, renderer-independent diagram IR. Normalization applies language defaults and makes containment, semantic kinds, edge directionality, and layout input explicit. It does not resolve themes or icons, solve layout, or contain renderer state.

The normative portable IR, diagnostic interchange, and conformance fixture contracts are defined in the [Stack Compiler Interchange Specification](./INTERCHANGE.md) and the JSON Schemas in [`schemas/`](./schemas). Canonical fixture data belongs to this specification repository. Implementations consume that data and record the specification release or revision they support.

## 12. Versioning and Backwards Compatibility

### 12.1 Language Version

Every document declares a `major.minor` language version, for example:

```stack
stack 1.0
```

The directive identifies the minimum language grammar and semantics required by that document. It is not the renderer version.

### 12.2 Specification Releases

Specification repository releases use semantic versioning:

- **Major** releases may make incompatible language changes.
- **Minor** releases add backwards-compatible language capabilities.
- **Patch** releases clarify wording, correct examples, and fix errata without changing valid source meaning.

The document directive omits the patch number because patch releases cannot introduce source-level capabilities.

### 12.3 Compatibility Rules

A renderer supporting language `M.N`:

- MUST accept every valid document declaring `M.n` where `n <= N`;
- MUST reject a document with a different major version;
- MUST reject a document with a higher minor version unless it explicitly supports that version;
- MUST NOT guess the meaning of unknown syntax from a newer version.

Within a stable major version, additions should be new optional properties, declarations, or enum values introduced in a later minor version. Existing syntax, defaults, and semantic meaning MUST NOT change incompatibly.

A document using a newly introduced feature must raise its declared minor version. A formatter MUST NOT raise the version unless it introduces or preserves a feature requiring the newer version.

### 12.4 Deprecation

A feature may be deprecated in a minor release but remains valid for the rest of that major version. Deprecation produces a warning with a mechanical replacement when one exists.

Removing or redefining a feature requires a new major version. Migration guides and before-and-after fixtures MUST accompany a major release. Old specifications and ADRs remain in repository history and MUST NOT be rewritten to hide previous behavior.

### 12.5 Draft Period

Before Stack 1.0 is accepted and tagged, this proposal may change incompatibly. Draft changes should still include rationale and example updates so implementers can follow the evolving contract.

## 13. Accessibility and Security Requirements

Renderers MUST derive accessible names from diagram, group, node, and edge text, not from identifiers or icon names. A non-visual representation SHOULD expose group containment and edge direction.

Source strings are untrusted plain text. Renderers that target HTML or SVG MUST escape them for the output context. Source must never be interpreted as HTML, Markdown, script, a file path, or a network URL.

Themes and icons MUST be loaded from the installed `@stack-sh/theme` catalog. A renderer must not interpret a theme or icon identifier as a file path, package name, or network location.

## 14. Examples

The files in [`examples/`](./examples) are canonical valid examples. They progress from minimal topology to a multi-boundary event-driven system.

### 14.1 Minimal

```stack
stack 1.0

diagram "Hello Stack" {
  node web "Web app"
  node api "API"
  edge web -> api
}
```

### 14.2 Node Semantics

```stack
stack 1.0

diagram "Application and datastore" {
  theme light

  node app "Application" {
    kind service
    icon "service"
    detail "Business logic"
  }

  node db "Primary database" {
    kind database
    icon "postgresql"
    detail "PostgreSQL"
  }

  edge app -> db "SQL" {
    kind data
  }
}
```

### 14.3 Groups and Layout

```stack
stack 1.0

diagram "Public application" {
  layout {
    direction right
  }

  group clients "Clients" {
    layout {
      direction down
      rank same [browser, mobile]
      order [browser, mobile]
    }

    node browser "Browser" {
      kind client
      icon "browser"
    }

    node mobile "Mobile app" {
      kind client
      icon "mobile"
    }
  }

  node gateway "Edge gateway" {
    icon "gateway"
  }

  group platform "Platform" {
    node api "Application API"
    node db "Primary database" {
      kind database
    }
  }

  edge browser -> gateway "HTTPS" {
    kind request
  }

  edge mobile -> gateway "HTTPS" {
    kind request
  }

  edge gateway -> api "HTTPS" {
    kind request
  }

  edge api -> db "SQL" {
    kind data
  }
}
```

### 14.4 Event-Driven Commerce Platform

```stack
stack 1.0

diagram "Commerce platform" {
  layout {
    direction right
  }

  node customer "Customer" {
    kind actor
  }

  group storefront "Storefront" {
    node web "Web storefront" {
      kind client
      icon "nextjs"
      detail "Next.js"
    }

    node gateway "Edge gateway" {
      icon "gateway"
    }
  }

  group commerce "Commerce services" {
    layout {
      direction down
      rank same [catalog, checkout]
      order [catalog, checkout]
    }

    node catalog "Catalog API" {
      detail "Products and pricing"
    }

    node checkout "Checkout API" {
      detail "Order orchestration"
    }
  }

  group asynchronous "Asynchronous processing" {
    node events "Event bus" {
      kind queue
    }

    node fulfillment "Fulfillment worker" {
      kind worker
    }

    node notifications "Notification worker" {
      kind worker
    }
  }

  group data "Data" {
    node products "Product database" {
      kind database
      icon "postgresql"
    }

    node orders "Order database" {
      kind database
      icon "postgresql"
    }

    node assets "Product media" {
      kind storage
    }
  }

  group partners "External systems" {
    node payment "Payment provider" {
      kind external
    }

    node email "Email provider" {
      kind external
    }
  }

  edge customer -> web "Browse and buy" {
    kind request
  }

  edge web -> gateway "HTTPS" {
    kind request
  }

  edge gateway -> catalog "Catalog requests" {
    kind request
  }

  edge gateway -> checkout "Checkout requests" {
    kind request
  }

  edge catalog -> products "SQL" {
    kind data
  }

  edge catalog -> assets "Media URLs" {
    kind data
  }

  edge checkout -> orders "Transactions" {
    kind data
  }

  edge checkout -> payment "Payment API" {
    kind request
  }

  edge checkout -> events "OrderPlaced" {
    kind event
  }

  edge events -> fulfillment "OrderPlaced" {
    kind event
  }

  edge events -> notifications "OrderPlaced" {
    kind event
  }

  edge notifications -> email "Send receipt" {
    kind request
  }
}
```
