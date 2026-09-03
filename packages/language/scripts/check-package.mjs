import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const { stdout } = await execFileAsync("npm", ["pack", "--json", "--dry-run"], {
  cwd: new URL("..", import.meta.url),
});
const result = JSON.parse(stdout);
const pack = Array.isArray(result) ? result[0] : result;
const actual = pack.files.map(({ path }) => path).sort();
const expected = [
  "LICENSE",
  "README.md",
  "grammar.d.ts",
  "grammars/stack.tmLanguage.json",
  "index.d.ts",
  "index.js",
  "language-configuration.d.ts",
  "language-configuration.json",
  "package.json",
].sort();

assert.deepEqual(actual, expected);
assert.equal(pack.name, "@stack-sh/language");
assert.equal(pack.version, "0.1.0");
