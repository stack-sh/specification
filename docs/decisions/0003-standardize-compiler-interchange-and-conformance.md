# ADR-0003: Standardize Compiler Interchange and Conformance Fixtures

## Status

Accepted

## Date

2026-09-02

## Context

Stack source is intended to be consumed by a reference Rust compiler, browser tools, command-line tools, editors, layout engines, and potentially independent implementations. The language specification currently defines source syntax and semantic diagnostics, but it does not define a portable normalized representation after parsing and validation.

Without a normative interchange contract, each compiler can choose different defaults, containment models, ordering rules, enum names, and optional-value behavior while still claiming to implement the same source language. Prose examples and implementation-specific unit tests are not sufficient to detect that drift.

Stack also needs a conformance suite that belongs to the language rather than to one implementation. The suite must be executable by any implementation and must avoid making human-readable diagnostic wording part of backwards compatibility.

## Decision

Stack will define two versioned JSON interchange documents:

- normalized diagram IR produced after successful language stages 1 through 4;
- structured diagnostics produced by any compiler stage.

JSON Schema Draft 2020-12 files in `schemas/` define their portable shapes. The normative field semantics, ordering guarantees, range conventions, and compatibility rules are defined in `INTERCHANGE.md`.

Normalized IR includes specification-defined defaults, explicit containment references, deterministic declaration order, and layout constraints or hints. It excludes source spans, comments, theme or icon resolution results, layout coordinates, renderer state, and filesystem or network handles.

Diagnostic interchange includes stable code, severity, message, an end-exclusive source range, an ordered expected-value list, optional help, and related information. Portable conformance expectations compare code, severity, and range. A fixture may additionally require exact expected values and ordering without making message, help, or related-information wording part of compatibility.

The specification repository owns conformance sources and expected documents. Each implementation owns its runner and records which specification revision or release it supports. Valid cases require normalized IR and may also expect warnings. Invalid cases require diagnostics and must not produce normalized IR.

Compiler-native APIs may use language-specific types. Conformance adapters map those types to the portable contract without requiring the core compiler to parse or serialize JSON at runtime.

## Alternatives Considered

### Use the Rust IR types as the only contract

- Pros: No additional schema or mapping layer.
- Cons: Couples every consumer and independent implementation to Rust naming and release mechanics.
- Rejected: The language contract must remain implementation-independent.

### Store only valid and invalid source files

- Pros: Very small fixture repository.
- Cons: Proves only acceptance or rejection; does not prove defaults, containment, directionality, ordering, or diagnostic locations.
- Rejected: Expected semantic outputs are necessary to detect meaningful drift.

### Compare complete diagnostic JSON byte for byte

- Pros: Maximally deterministic output.
- Cons: Makes message improvements and implementation-specific corrective guidance breaking changes.
- Rejected: Portable meaning is carried by code, severity, and source range.

### Let the specification CI depend directly on the Rust compiler

- Pros: One place executes the reference implementation.
- Cons: Makes the language repository depend on one implementation and blocks intentional specification changes until that implementation is updated.
- Rejected: Implementations consume the suite; the specification remains implementation-neutral.

### Include resolved themes, icons, or layout geometry in normalized IR

- Pros: One document could be passed directly to SVG rendering.
- Cons: Mixes language normalization with catalog versions, visual metrics, and renderer-specific algorithms.
- Rejected: Those stages are downstream of the compiler interchange boundary.

## Consequences

- Independent implementations can demonstrate equivalent source semantics with one canonical suite.
- Layout and renderer projects receive an explicit, versioned input contract.
- Compiler implementations need a small adapter for conformance JSON.
- Expected IR documents are reviewable but must be updated whenever a normative default or field changes.
- A backwards-incompatible interchange change requires a new interchange major version even when source syntax is unchanged.
- Specification revisions can land before implementations support them; each implementation must identify the revision or release it tests.
