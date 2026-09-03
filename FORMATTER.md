# Stack Canonical Formatter Specification

## 1. Status and Scope

This document is a normative part of the draft Stack 1.0 specification. It defines the one canonical byte representation of a lexically and syntactically valid `.stack` document.

A canonical formatter accepts UTF-8 Stack source without a byte order mark. It MUST reject a document that produces a lexical or syntax error and MUST NOT present partial rewritten source as a successful result. Semantic and complexity diagnostics do not prevent formatting, and successful formatting does not imply that the document is semantically valid.

Formatting MUST preserve every line comment. When a document produces normalized IR, its canonical output MUST produce semantically equal normalized IR. When a syntactically valid document produces semantic or complexity errors, the set of portable diagnostic codes before and after formatting MUST be identical. Formatting never changes the declared language version.

## 2. Canonical Output

Canonical output MUST:

- be UTF-8 without a byte order mark;
- use LF (`U+000A`) for every line ending, regardless of the input line endings;
- use ASCII spaces, never tabs, for formatting whitespace;
- contain no formatting whitespace at the end of a line;
- end with exactly one LF.

Whitespace inside a line comment is comment text rather than formatting whitespace and is preserved as described in [Section 6](#6-comments).

## 3. Indentation and Lines

Each block increases indentation by two ASCII spaces. The version directive and diagram declaration have zero indentation. A closing brace has the same indentation as the declaration that opened its block.

Absent a comment between two tokens that would otherwise share a line, the formatter MUST put each of the following on one line:

- the version directive;
- a diagram, group, node, or edge declaration header, including its opening brace when present;
- a theme statement;
- a node or edge property;
- a layout statement.

Opening braces are preceded by one ASCII space and remain on the declaration or `layout` line. Closing braces are on their own line. There is no blank line immediately after an opening brace or immediately before its closing brace.

The canonical token spacing is:

```stack
stack 1.0

diagram "Title" {
  theme dark

  node client "Client"

  group services "Services" {
    node api "API" {
      kind service
      icon "service"
      detail "Public API"
    }
  }

  edge client -> api "HTTPS" {
    kind request
  }

  layout {
    direction right
    rank same [client, services]
    order [client, services]
  }
}
```

The formatter MUST use one ASCII space at the positions shown above, no space around the version dot, and no space just inside brackets.

## 4. Blank Lines

The version directive and diagram declaration are separated by exactly one empty line.

Adjacent members of a diagram or group body are separated by exactly one empty line. A member is a node, group, edge, theme, or layout construct. Properties in node and edge blocks and statements in layout blocks have no empty lines between them.

Leading comments belong to the member or statement that follows them. A separator is placed before the first leading comment, not between that comment and its member. A trailing comment belongs to the preceding line, so any separator follows the comment.

No other empty lines are emitted.

## 5. Order, Lists, and Strings

### 5.1 Order

The formatter MUST preserve the authored order of:

- diagram and group members, including the position of theme and layout constructs;
- node and edge properties;
- layout statements;
- identifiers in `rank same` and `order` lists.

It MUST NOT group or sort declarations or properties. This preserves declaration-order data in normalized IR and keeps comments attached to the same token boundaries.

### 5.2 Identifier Lists

An identifier list is emitted on one line as an opening bracket, the identifiers in authored order separated by a comma and one ASCII space, and a closing bracket. No trailing comma is emitted.

```stack
rank same [frontend, backend]
order [frontend, backend]
```

### 5.3 Strings

The formatter decodes each valid source string and emits its Unicode scalar values without Unicode normalization. A double quote is emitted as `\"`, a backslash is emitted as `\\`, and every other permitted scalar value is emitted directly as UTF-8. Canonical output therefore does not use `\uXXXX` escapes.

For example, `"API \u56F3 \uD83D\uDE80"` becomes `"API 図 🚀"`, while decoded quote and backslash characters remain escaped.

## 6. Comments

The bytes from `//` through the byte before its line ending form the comment lexeme. The formatter MUST preserve that lexeme exactly and MUST preserve comment order. It also MUST preserve the comment's gap between the same preceding and following non-comment tokens; string canonicalization does not change token identity for this rule.

A comment is **trailing** when a non-comment token precedes it on the same input line. A trailing comment is emitted immediately after its preceding token, preceded by one ASCII space. The line ends immediately after the comment lexeme. If another token in the same construct follows the comment, formatting resumes on the next line using the continuation indentation defined below.

Every other comment is an **own-line** comment. Consecutive own-line comments at one token gap remain consecutive, use the indentation of the following member, statement, or property, and are emitted immediately before it. If the next token closes a block, the comments use the indentation of that block's members. If the next token is end-of-file, they use zero indentation.

A comment may occur at a token gap inside a construct that canonical formatting would otherwise place on one line. The comment remains at that token gap and forces a line break. The comment and the remaining tokens use one additional indentation level relative to the construct's first line when they do not already have a greater block indentation. This comment-forced continuation is the only exception to the one-line rules in [Section 3](#3-indentation-and-lines).

Comments before the version directive form its leading comment block. Comments after the diagram's closing brace form a final own-line comment block separated from the diagram by one empty line.

## 7. Conformance Fixtures

Canonical formatter cases live in `conformance/formatter/`. Each case directory contains exactly:

```text
conformance/formatter/<case-id>/input.stack
conformance/formatter/<case-id>/expected.stack
conformance/formatter/<case-id>/expected.ir.json
```

For every case, a conforming formatter runner MUST:

1. format `input.stack` and compare the output bytes exactly with `expected.stack`;
2. format `expected.stack` and require byte-identical `expected.stack` output, proving idempotence;
3. compile both `input.stack` and `expected.stack` with compiler stages enabled and catalog, layout, and renderer stages disabled;
4. require both compilations to produce no compiler-stage error;
5. compare both normalized IR documents semantically with `expected.ir.json`, proving semantic preservation;
6. record the specification release or commit revision used for the run.

JSON object-member order and JSON whitespace are not significant. Array order is significant. A warning does not invalidate a formatter case, but portable diagnostic code, severity, and range are not compared across formatting because canonical whitespace changes source ranges.
