# ADR-0006: Standardize Protocol-Neutral Language Intelligence

## Status

Accepted

## Date

2026-09-05

## Context

Stack diagnostics, completion, hover, document symbols, and formatting will be consumed by a native language server, the browser playground, the CLI, and agents. If each integration defines its own positions, completion meanings, partial-document behavior, or text edits, the same source will behave differently across products.

The Language Server Protocol is an important adapter target, but its JSON-RPC lifecycle, negotiated position encoding, capabilities, and incremental document synchronization are transport concerns. Making LSP types the compiler API would couple browser and non-editor consumers to one protocol and would put mutable document state in the dependency-free compiler core.

Stack already has portable diagnostics and end-exclusive UTF-8 source ranges. The compiler also has a lossless source model and semantic source-map sidecar. These contracts provide the correct foundation for language features without changing normalized IR.

## Decision

Define language-intelligence schema version 1.0 in the specification repository. Requests and responses are protocol-neutral, identify one caller-owned document version, and cover diagnostics, completion, hover, document symbols, and format edits.

All portable positions reuse the existing zero-based UTF-8 byte offset plus one-based Unicode scalar line and column. Protocol adapters convert their client coordinates at the boundary. Responses echo the document version so callers can suppress stale work.

The compiler remains stateless and dependency-free. It owns semantic diagnostics, completion, hover, and document symbols over one complete source snapshot. It exposes native types and does not parse or serialize JSON at runtime. Completion catalog entries are explicit caller-owned data; the compiler never loads themes or provider packs.

The canonical formatter owns formatted source and maps a changed result to non-overlapping text edits. A WebAssembly adapter owns validated JavaScript / JSON serialization. A native LSP adapter owns JSON-RPC, incremental document state, cancellation, position conversion, and capability negotiation. Both adapters consume the same compiler semantics and canonical fixtures.

The specification repository owns JSON Schemas and fixtures. Each implementation pins the exact specification revision it passes.

## Alternatives Considered

### Use LSP types as the compiler contract

- Pros: A native language server would require less mapping code.
- Cons: Couples every consumer to JSON-RPC-era position, capability, and lifecycle choices; browser and agent callers inherit editor protocol concerns.
- Rejected: LSP is an adapter boundary, not Stack language semantics.

### Put language intelligence in the Web application

- Pros: The first interactive consumer could ship quickly.
- Cons: Native tools would duplicate parsing and behavior, while product UI would become the accidental language owner.
- Rejected: Shared semantic behavior belongs below product integrations.

### Make the compiler retain incremental documents

- Pros: The core could optimize reparsing immediately.
- Cons: Introduces mutable lifecycle, version, cancellation, and memory-policy concerns before performance evidence requires them.
- Rejected: A stateless snapshot contract is deterministic and leaves future incremental internals additive.

### Serialize JSON from the compiler library

- Pros: Adapters could forward one ready-made payload.
- Cons: Adds a runtime dependency and commits the native API to one serialization library.
- Rejected: Native types plus conformance-only adapters preserve a smaller core.

### Allow Markdown hover and completion documentation

- Pros: Rich editor presentation.
- Cons: Creates rendering and injection risk and makes consumers disagree about supported markup.
- Rejected: Portable prose is plain text; adapters may add trusted presentation outside the semantic contract.

## Consequences

- Native, WebAssembly, CLI, editor, and agent consumers can compare the same semantic fixture output.
- LSP adapters perform explicit coordinate and lifecycle conversion instead of leaking protocol types into the compiler.
- Completion catalogs remain caller-owned and can include installed provider icons without adding I/O to compiler code.
- Snapshot analysis may reparse complete documents initially; incremental compiler internals can be added later without changing the public operation model.
- Format edits share one data model while canonical formatting remains owned by the formatter.
- New optional language features can evolve within schema 1.x; breaking observable behavior requires a new major schema.
