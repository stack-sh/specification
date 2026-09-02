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

## Comparison

- JSON values are compared semantically; formatting and object-member order do not matter.
- Array order is significant.
- A valid case must produce the expected normalized IR.
- An absent valid-case diagnostic file means no portable diagnostics are expected.
- An invalid case must not produce normalized IR.
- Diagnostic expectations compare code, severity, and range in emitted order.
- Diagnostic message, help, and related-information wording are not compared.

The complete normative behavior is defined in the [Stack Compiler Interchange Specification](../INTERCHANGE.md).
