# ADR-0002: Make the Canonical Theme Catalog Own Icons

## Status

Accepted

## Date

2026-09-02

## Context

Stack diagrams select one visual theme. Icons are part of that visual system: an SVG designed for a light background may not remain legible, balanced, or stylistically appropriate in a dark theme. Treating icons as one renderer-wide catalog would separate icon artwork from the theme responsible for its palette and visual language.

Stack also needs predictable identifiers for open source theme contributions. Requiring contributor or package namespaces would make authored diagrams noisier and would preserve ownership details that do not contribute to diagram meaning.

The current Stack 1.0 limits of 40 nodes, 12 groups, three group levels, and at most twice as many edges as nodes are accepted as the initial readability budget. Authored node details are intentional diagram content and must not disappear in compact or alternate themes.

## Decision

`@stack-sh/theme` will be the canonical, versioned, open source catalog for both themes and their icon assets.

One diagram selects exactly one effective theme. Each theme owns zero or more named icons, forming a one-to-many relationship from theme to icon assets. Stack source refers to a logical icon with a theme-local identifier such as `"postgresql"`; it does not name an icon provider or SVG file.

The same logical icon identifier may resolve to different SVG artwork in different themes. When multiple themes implement the same identifier, it must continue to represent the same logical subject. Every theme must provide a fallback visual treatment for every Stack node kind so a missing named icon never prevents rendering.

Core icon names and SVG assets will not be defined by the Stack language specification. They belong to `@stack-sh/theme` and evolve with that package.

Theme identifiers are global, unnamespaced Stack identifiers. The first catalog pull request merged for an identifier registers it. Once registered, an identifier cannot be reassigned to a different theme, including after deprecation or removal.

When `detail` is authored on a node, every renderer and theme must display it as visible diagram content. Tooltip-only or metadata-only treatment is not conforming.

The current diagram complexity limits are retained for Stack 1.0.

## Catalog Review Workflow

The `@stack-sh/theme` repository should validate every contribution automatically. Its pull request workflow should:

1. Reject duplicate or previously reserved theme identifiers.
2. Validate theme metadata and SVG safety requirements.
3. Render representative Stack fixtures with the proposed theme.
4. Post the generated SVG previews to the pull request for visual review.

This workflow is catalog governance, not Stack language syntax. It is recorded here because fast visual review is part of the rationale for using one canonical open source catalog.

## Alternatives Considered

### Use one global icon asset across every theme

- Pros: Small catalog and simple caching.
- Cons: One SVG may not work across light, dark, high-contrast, or stylistically distinct themes.
- Rejected: Theme-specific artwork is necessary for reliable visual quality.

### Maintain independent icon-provider namespaces

- Pros: Existing providers could publish icons without contributing to the theme catalog.
- Cons: Requires namespace registration, allows icon styling to diverge from the selected theme, and exposes provider details in Stack source.
- Rejected: The selected theme is the correct icon resolution scope.

### Namespace theme identifiers by contributor

- Pros: Avoids global naming conflicts and makes ownership explicit.
- Cons: Produces longer source and makes stable diagram identifiers depend on contributor identity.
- Rejected: First accepted registration is simpler; registered names remain permanently reserved.

### Allow themes to hide node details in compact output

- Pros: Smaller node cards and denser diagrams.
- Cons: Removes content the author explicitly placed in the diagram and makes meaning depend on output mode.
- Rejected: Authored details remain visible.

## Consequences

- Switching themes can change icon artwork without changing Stack source or topology.
- Theme authors are responsible for coherent icon artwork and node-kind fallbacks.
- Missing named icons produce a warning and use the selected theme's node-kind fallback.
- The installed `@stack-sh/theme` version can change visual output, so renderers should record it in output metadata.
- Theme names are concise and stable, but catalog maintainers must enforce first-merged registration and permanent reservation.
- Automated SVG previews make visual review fast without moving styling controls into the DSL.
