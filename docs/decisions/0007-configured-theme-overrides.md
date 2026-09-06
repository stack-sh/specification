# ADR 0007: Let host configuration override theme palettes

## Status

Accepted

## Context

Stack diagrams need reusable organization-specific colors without adding visual values to source, duplicating complete catalog themes, or allowing arbitrary CSS and assets. The public catalog also has a first-merged identifier rule, while users reasonably expect a local `default` definition to become their effective default.

Treating a configured `default` as an error would force a separate selection flag or a new source identifier. Letting configured themes extend one another would instead introduce ordering, recursion, and cycle handling that the initial palette-only feature does not need.

## Decision

Host configuration may supply named theme overrides. A configured name may intentionally match an installed catalog theme and takes precedence during theme selection.

Each override extends exactly one installed builtin theme: `default`, `light`, or `dark`. The host resolves every base from the installed catalog before registering any override, so `default` extending `default` is deterministic and non-recursive. An override may replace only the nine semantic palette colors. Typography, node-kind visuals, connector geometry, icons, and provenance remain inherited from the builtin base.

Omitting the source theme statement still requests `default`. If configuration contains a `default` override, that override is selected. Missing names retain `STK6001` and fall back to the effective `default`.

The theme catalog contract owns the portable override shape, validation, normalization, and effective revision algorithm. Native and browser hosts supply only validated caller-owned data to the pure engine. No theme name triggers filesystem or network discovery.

## Consequences

- Existing sources and hosts without theme overrides keep their current behavior.
- A user's configuration can deliberately change `default`, `light`, `dark`, or another installed theme without changing Stack source.
- Rendered appearance can depend on host configuration, so metadata must identify the effective catalog revision.
- User-configured colors are preserved exactly; hosts surface contrast concerns instead of silently rewriting them.
- Older hosts may reject the new configuration key, and documentation must identify the first supporting release.
- Changing the shipped builtin palettes remains a catalog change rather than a user-configured override.
