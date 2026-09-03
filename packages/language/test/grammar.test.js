import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { createHighlighterCore } from "@shikijs/core";
import { createJavaScriptRegexEngine } from "@shikijs/engine-javascript";

import { languageConfiguration, stackLanguage } from "@stack-sh/language";
import rawGrammar from "@stack-sh/language/grammar" with { type: "json" };
import rawLanguageConfiguration from "@stack-sh/language/language-configuration" with { type: "json" };

const colors = {
  comment: "#110001",
  declaration: "#220002",
  property: "#330003",
  value: "#440004",
  string: "#550005",
  escape: "#660006",
  invalid: "#770007",
  number: "#880008",
  operator: "#990009",
  punctuation: "#AA000A",
  identifier: "#BB000B",
};

const testTheme = {
  name: "stack-test",
  type: "light",
  colors: {
    "editor.background": "#ffffff",
    "editor.foreground": "#000000",
  },
  tokenColors: [
    {
      scope: "comment.line.double-slash.stack",
      settings: { foreground: colors.comment },
    },
    {
      scope: "keyword.control.declaration.stack",
      settings: { foreground: colors.declaration },
    },
    {
      scope: "keyword.other.property.stack",
      settings: { foreground: colors.property },
    },
    {
      scope: "constant.language.stack",
      settings: { foreground: colors.value },
    },
    {
      scope: "string.quoted.double.stack",
      settings: { foreground: colors.string },
    },
    {
      scope: "constant.character.escape.stack",
      settings: { foreground: colors.escape },
    },
    {
      scope: "invalid.illegal.escape.stack",
      settings: { foreground: colors.invalid },
    },
    {
      scope: "constant.numeric.integer.stack",
      settings: { foreground: colors.number },
    },
    {
      scope: "keyword.operator.edge.stack",
      settings: { foreground: colors.operator },
    },
    {
      scope: "punctuation.stack",
      settings: { foreground: colors.punctuation },
    },
    {
      scope: "variable.other.identifier.stack",
      settings: { foreground: colors.identifier },
    },
  ],
};

function findToken(lines, lineIndex, content) {
  const token = lines[lineIndex].find((candidate) => candidate.content === content);
  assert.ok(token, `expected token ${JSON.stringify(content)} on line ${lineIndex + 1}`);
  return token;
}

function createTestHighlighter() {
  return createHighlighterCore({
    themes: [testTheme],
    langs: [stackLanguage],
    engine: createJavaScriptRegexEngine(),
  });
}

test("exports portable editor metadata", () => {
  assert.equal(stackLanguage.name, "stack");
  assert.deepEqual(rawGrammar, stackLanguage);
  assert.equal(stackLanguage.scopeName, "source.stack");
  assert.deepEqual(stackLanguage.fileTypes, ["stack"]);
  assert.equal(languageConfiguration.comments.lineComment, "//");
  assert.deepEqual(rawLanguageConfiguration, languageConfiguration);
  assert.deepEqual(languageConfiguration.brackets, [
    ["{", "}"],
    ["[", "]"],
  ]);
});

test("tokenizes Stack syntax with the pure JavaScript regex engine", async () => {
  const highlighter = await createTestHighlighter();

  const source = `stack 1.0
diagram "Checkout" {
  // contextual keywords remain legal identifiers
  node api-service "Checkout API" {
    kind service
    detail "handles \\u2713 and invalid \\q"
  }
  edge client -> api-service "HTTPS"
  layout { direction right }
}`;
  const lines = highlighter.codeToTokensBase(source, {
    lang: "stack",
    theme: "stack-test",
  });

  assert.equal(findToken(lines, 0, "stack").color, colors.declaration);
  assert.equal(findToken(lines, 0, "1").color, colors.number);
  assert.equal(findToken(lines, 0, ".").color, colors.punctuation);
  assert.equal(findToken(lines, 1, "diagram").color, colors.declaration);
  assert.equal(findToken(lines, 1, '"Checkout"').color, colors.string);
  assert.equal(
    findToken(lines, 2, "// contextual keywords remain legal identifiers").color,
    colors.comment,
  );
  assert.equal(findToken(lines, 3, "api-service").color, colors.identifier);
  assert.equal(findToken(lines, 4, "kind").color, colors.property);
  assert.equal(findToken(lines, 4, "service").color, colors.value);
  assert.equal(findToken(lines, 5, "\\u2713").color, colors.escape);
  assert.equal(findToken(lines, 5, "\\q").color, colors.invalid);
  assert.equal(findToken(lines, 7, "->").color, colors.operator);
  assert.equal(findToken(lines, 8, "direction").color, colors.property);
  assert.equal(findToken(lines, 8, "right").color, colors.value);

  highlighter.dispose();
});

test("classifies every contextual keyword declared by Stack 1.0", async () => {
  const expected = new Map([
    ...["stack", "diagram", "group", "node", "edge", "theme", "layout"].map((word) => [
      word,
      colors.declaration,
    ]),
    ...["kind", "icon", "detail", "direction", "rank", "same", "order"].map((word) => [
      word,
      colors.property,
    ]),
    ...[
      "right",
      "down",
      "actor",
      "client",
      "service",
      "function",
      "worker",
      "database",
      "cache",
      "queue",
      "storage",
      "external",
      "flow",
      "request",
      "event",
      "data",
      "dependency",
    ].map((word) => [word, colors.value]),
  ]);
  const specification = await readFile(
    new URL("../../../SPECIFICATION.md", import.meta.url),
    "utf8",
  );
  const keywordSection = specification.match(
    /### 5\.1 Contextual Keywords[\s\S]*?```text\n([^`]+)```/,
  );
  assert.ok(keywordSection, "expected the Stack 1.0 contextual keyword list");
  const normativeKeywords = keywordSection[1].trim().split(/\s+/).sort();
  assert.deepEqual([...expected.keys()].sort(), normativeKeywords);

  const highlighter = await createTestHighlighter();
  for (const [word, color] of expected) {
    const lines = highlighter.codeToTokensBase(word, {
      lang: "stack",
      theme: "stack-test",
    });
    assert.equal(findToken(lines, 0, word).color, color, word);
  }
  highlighter.dispose();
});
