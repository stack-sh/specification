# ADR 0005: Separate provider icon namespaces from theme icons

## Status

Accepted

## Context

Stack 1.0 originally allowed only unnamespaced icon identifiers resolved by the selected theme. Architecture diagrams also need exact provider products such as Amazon S3 without changing the node's semantic `kind`. Provider artwork has source-specific copyright, trademark, redistribution, modification, attribution, and lifecycle terms that cannot be inherited from Stack's Apache-2.0 code.

## Decision

Stack accepts either an unnamespaced theme icon or one `<provider>:<icon>` identifier. Provider namespaces are lowercase, explicit, and cannot override a theme icon or another provider namespace.

Provider packs are separate caller-supplied resources. A renderer does not discover, download, upload, or cache a pack. It preserves the authored node kind, uses the existing kind fallback with `STK5001` when a pack or icon is unavailable, and records the exact pack and asset provenance when provider artwork is embedded.

The provider-pack manifest, validation, and rights boundary are owned by `stack-sh/theme`. Language implementations validate only the symbolic identifier shape; they do not infer a file, package, URL, or license from it.

## Consequences

- Existing unnamespaced documents and theme behavior remain valid.
- A specific provider product can use stable source syntax without assigning vendor semantics to `kind`.
- Hosts must install or import provider packs explicitly and comply with their separate terms.
- Native and browser renderers can share the same pure in-memory resolution behavior.
- Missing provider resources remain warnings with deterministic core fallbacks.
