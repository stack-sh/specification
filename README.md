# Stack Language Specification

Stack is an opinionated DSL for describing software architecture and technology-stack diagrams. It is designed to be concise enough for humans and language models to write, while remaining constrained enough for renderers to produce consistently polished diagrams.

This repository is the canonical source for the Stack language. It defines the language contract; it does not contain a renderer, server, editor, or CLI.

## Status

The language is currently a proposal for Stack 1.0. No compatibility guarantee applies until the specification is accepted and tagged as 1.0.0.

## Documents

- [Language specification](./SPECIFICATION.md)
- [Compiler interchange specification](./INTERCHANGE.md)
- [ADR-0001: Adopt a constrained declarative topology language](./docs/decisions/0001-constrained-declarative-language.md)
- [ADR-0002: Make the canonical theme catalog own icons](./docs/decisions/0002-theme-owned-icons.md)
- [ADR-0003: Standardize compiler interchange and conformance fixtures](./docs/decisions/0003-standardize-compiler-interchange-and-conformance.md)
- [Examples](./examples)
- [Conformance suite](./conformance)

## Example

```stack
stack 1.0

diagram "Checkout" {
  theme light

  node browser "Customer browser" {
    kind client
    icon "browser"
  }

  node api "Checkout API" {
    detail "TypeScript"
  }

  node database "Orders" {
    kind database
    icon "postgresql"
  }

  edge browser -> api "HTTPS" {
    kind request
  }

  edge api -> database "SQL" {
    kind data
  }
}
```

Stack sources conventionally use the `.stack` extension.

## Validation

Install the development requirements and validate the portable schemas and conformance data:

```sh
python -m pip install --requirement requirements-dev.txt
check-jsonschema --check-metaschema schemas/*.json
check-jsonschema --schemafile schemas/normalized-ir.schema.json conformance/valid/*/expected.ir.json
find conformance -name expected.diagnostics.json -print0 | xargs -0 check-jsonschema --schemafile schemas/diagnostic-expectations.schema.json
```

## Design Principles

- Describe architecture, not pixels.
- Prefer one obvious representation over flexible shorthand.
- Keep source deterministic, diffable, and safe to generate.
- Make semantic mistakes explicit instead of silently guessing.
- Let renderers choose typography, spacing, color, routing, and responsive composition within the selected theme.
- Resolve themes and their one-to-many icon collections from `@stack-sh/theme`.
- Evolve additively within a language major version.

## Contributing

The language contract must be changed before implementations adopt new syntax or semantics. A language change should include:

1. A specification update.
2. Valid and invalid examples when applicable.
3. Compatibility and migration notes.
4. An ADR for decisions that are costly to reverse.

All repository content, issues, and pull requests should be written in English.
