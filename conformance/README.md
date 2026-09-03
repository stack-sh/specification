# Stack Conformance Suite

This directory contains implementation-independent compiler conformance cases for the Stack language.

## Layout

Each case is a directory with a lowercase ASCII identifier:

```text
valid/<case-id>/source.stack
valid/<case-id>/expected.ir.json
valid/<case-id>/expected.diagnostics.json  # optional

invalid/<case-id>/source.stack
invalid/<case-id>/expected.diagnostics.json
```

`source.stack` must be read as bytes. This permits future encoding-error fixtures even though valid Stack documents are UTF-8.

Expected IR documents conform to [`normalized-ir.schema.json`](../schemas/normalized-ir.schema.json). Diagnostic expectation documents conform to [`diagnostic-expectations.schema.json`](../schemas/diagnostic-expectations.schema.json).

The canonical suite covers every Stack 1.0 diagnostic assigned to compiler stages 1 through 4: `STK1001` through `STK3014`, excluding unassigned numbers, plus `STK4002` and `STK4003`. [`validate-compiler-diagnostics.py`](../scripts/validate-compiler-diagnostics.py) verifies that every required code occurs in at least one expectation document. Renderer-stage `STK4001`, `STK5001`, and `STK6001` remain outside compiler conformance.

The encoding cases intentionally include raw invalid UTF-8, a UTF-8 byte order mark, CRLF line endings, and a Unicode scalar before an error position. Tools must preserve `source.stack` bytes rather than decoding and rewriting fixtures during discovery.

## Comparison

- JSON values are compared semantically; formatting and object-member order do not matter.
- Array order is significant.
- A valid case must produce the expected normalized IR.
- An absent valid-case diagnostic file means no portable diagnostics are expected.
- An invalid case must not produce normalized IR.
- Diagnostic expectations compare code, severity, and range in emitted order.
- Diagnostic message, help, and related-information wording are not compared.

The complete normative behavior is defined in the [Stack Compiler Interchange Specification](../INTERCHANGE.md).
