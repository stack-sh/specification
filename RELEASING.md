# Releasing `@stack-sh/language`

The package is public and is released from this public repository. Release artifacts must come from a merged `main` revision whose `conformance-data` and `language-package` checks have passed.

## First release

The npm package must exist before its trusted publisher can be configured. An authenticated maintainer with publish access to the `@stack-sh` scope performs the one-time bootstrap from a clean `main` checkout:

```sh
npm ci
npm run test:language
npm run typecheck:language
npm run pack:check
npm publish --workspace @stack-sh/language --access public
```

After `@stack-sh/language` exists on npm, configure its trusted publisher with these exact values:

- Provider: GitHub Actions
- Organization: `stack-sh`
- Repository: `specification`
- Workflow filename: `release-language.yaml`
- Allowed action: `npm stage publish`

Then create the `language-v0.1.0` GitHub Release from the same merged revision. The release workflow recognizes that the package version already exists and completes without staging it twice.

## Subsequent releases

1. Update the language package version in a pull request.
2. Run the complete repository checks and merge the pull request.
3. Create a GitHub Release whose tag is exactly `language-v<package version>` and targets the merged commit.
4. Verify that the release workflow stages the package through npm trusted publishing.
5. Inspect the staged package on npm, then approve it with two-factor authentication.
6. Verify the public registry metadata, provenance, and a clean consumer import.

The workflow rejects a tag that does not match the package version. It validates the package again on the tagged revision, uses no long-lived npm token, and leaves npm provenance enabled. A package does not become public until a maintainer explicitly approves the staged version with two-factor authentication.
