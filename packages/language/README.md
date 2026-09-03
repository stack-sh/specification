# `@stack-sh/language`

Editor language assets for the [Stack diagram language](https://github.com/stack-sh/specification).

The package contains the shared TextMate grammar and editor language configuration. It deliberately has no runtime dependency on a syntax highlighter, editor, theme, compiler, or language server.

## Usage with Shiki

```js
import { createHighlighterCore } from "shiki/core";
import { createJavaScriptRegexEngine } from "shiki/engine/javascript";
import githubLight from "@shikijs/themes/github-light";
import { stackLanguage } from "@stack-sh/language";

const highlighter = await createHighlighterCore({
  themes: [githubLight],
  langs: [stackLanguage],
  engine: createJavaScriptRegexEngine(),
});

const html = highlighter.codeToHtml(source, {
  lang: "stack",
  theme: "github-light",
});
```

Raw JSON assets are also exported as `@stack-sh/language/grammar` and `@stack-sh/language/language-configuration`.

## Boundaries

TextMate scopes classify source for presentation. They do not determine whether a document is valid. Use the Stack compiler or engine for parsing and diagnostics.

Stack 1.0 keywords are contextual, so a keyword remains legal where an identifier is expected. The lexical grammar highlights keyword-shaped tokens consistently without attempting to reproduce parser context.
