# Stack example catalog

[`catalog.json`](./catalog.json) is the versioned index for the curated Stack example corpus. Its contract is defined by [`example-catalog.schema.json`](../schemas/example-catalog.schema.json).

Each entry links to one canonical `.stack` source and records:

- the learning stage and intended use;
- required caller-owned provider icon packs;
- represented syntax features;
- the expected node, group, and edge structure;
- accessible alternative text for a generated thumbnail.

Consumers such as the Web gallery, CLI starter templates, layout fixtures, and machine-readable distribution should pin a specification commit and reuse these sources. A consumer may keep a generated snapshot for a hermetic build, but it must verify every copied source against the pinned catalog rather than maintaining an independent example.

Provider names identify caller-owned packs. The corpus contains provider icon identifiers, not provider artwork, licenses, or terms acceptance. Consumers must resolve those identifiers through validated local packs and preserve the provider boundary defined by the specification.
