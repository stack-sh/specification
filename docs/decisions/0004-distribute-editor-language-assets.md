# ADR-0004: Distribute Shared Editor Language Assets from the Specification

## Status

Accepted

## Date

2026-09-03

## Context

Stack source is edited in the browser playground today and may later appear in documentation code blocks, desktop editors, and IDE extensions. These consumers need consistent lexical classification for comments, strings, declarations, properties, enum values, operators, numbers, punctuation, and identifiers.

A TextMate grammar is a presentation-oriented description of the language's lexical surface. It is useful to many editor integrations, but it cannot enforce Stack semantics and must not become a second language definition. Stack 1.0 also has contextual keywords, so lexical highlighting cannot always reproduce parser context.

Placing the grammar in a future language-server repository would make editor presentation depend on a protocol server and encourage that server to own syntax. Placing separate copies in the Web and editor repositories would allow the copies to drift.

## Decision

The specification repository owns and tests shared editor language assets under `packages/language` and distributes them as the public `@stack-sh/language` npm package.

The package contains:

- a TextMate grammar with the stable root scope `source.stack`;
- a portable editor language configuration for comments, brackets, surrounding pairs, and identifier words;
- dependency-free JavaScript and TypeScript entry points for consuming those assets.

The normative prose grammar in `SPECIFICATION.md` remains authoritative. The TextMate grammar follows that contract and only classifies source for presentation. Highlighting never establishes that a token or document is valid.

The package does not depend on Shiki, an editor runtime, a theme, the Stack compiler, or an LSP implementation. Consumers select those integrations themselves and pin a released package version.

The reference compiler continues to own parsing, semantic validation, structured diagnostics, source ranges, and normalized IR. A future language server will own LSP document lifecycle and protocol features such as completion, hover, navigation, and diagnostic publication. It will consume compiler capabilities and this package rather than defining a separate Stack grammar.

## Alternatives Considered

### Put the grammar in the Web repository

- Pros: The first consumer can evolve quickly.
- Cons: Documentation and editor integrations must copy or depend on a product-specific repository.
- Rejected: The grammar represents shared language tooling, not Web UI behavior.

### Put the grammar in a future LSP repository

- Pros: Most editor-facing assets would be colocated.
- Cons: Syntax highlighting would depend organizationally on a protocol integration that does not yet exist, and non-LSP consumers would inherit that coupling.
- Rejected: The language server consumes the language contract; it does not own it.

### Generate the grammar from the EBNF

- Pros: Reduces duplicated keyword lists in principle.
- Cons: TextMate scopes, string recovery, and contextual-keyword approximation require presentation decisions that the normative EBNF does not express.
- Rejected for Stack 1.0: Tests and review provide a smaller and clearer synchronization mechanism. Generation can be reconsidered if the grammar grows substantially.

### Publish a Shiki-specific package

- Pros: Gives the Web consumer a ready-made highlighter.
- Cons: Couples shared language data to one runtime, theme strategy, and release cadence.
- Rejected: The package should remain usable by Shiki, VS Code-compatible tooling, and other TextMate consumers.

## Consequences

- Web, documentation, and editor integrations can share one versioned grammar.
- Grammar changes are reviewed beside language changes and can be tested with specification examples.
- Consumers must provide their own highlighter and visual theme.
- Contextual keywords may be highlighted as keywords even where the parser accepts them as identifiers; this is presentation behavior, not a semantic restriction.
- Compiler and language-server implementations must not use TextMate scopes as parser input.
