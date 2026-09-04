#!/usr/bin/env python3

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
CATALOG_PATH = EXAMPLES / "catalog.json"


def count_declarations(source: str, declaration: str) -> int:
    return len(re.findall(rf"^\s*{declaration}\s+", source, re.MULTILINE))


def represented_features(source: str) -> set[str]:
    features = set()
    patterns = {
        "themes": r"^\s*theme\s+",
        "node-kinds": r"^\s*node\s+[^\n{]+\{[^{}]*^\s*kind\s+",
        "node-details": r"^\s*detail\s+",
        "groups": r"^\s*group\s+",
        "layout-direction": r"^\s*direction\s+",
        "rank-constraints": r"^\s*rank\s+same\s+",
        "order-constraints": r"^\s*order\s+",
        "edge-labels": r'^\s*edge\s+[^\n]+\s+"[^\n]+"\s*\{',
        "edge-kinds": r"^\s*edge\s+[^\n{]+\{[^{}]*^\s*kind\s+",
        "directed-edges": r"^\s*edge\s+\S+\s+->\s+\S+",
        "bidirectional-edges": r"^\s*edge\s+\S+\s+<->\s+\S+",
        "association-edges": r"^\s*edge\s+\S+\s+--\s+\S+",
        "provider-icons": r'^\s*icon\s+"[a-z][a-z0-9-]+:',
    }
    for feature, pattern in patterns.items():
        if re.search(pattern, source, re.MULTILINE | re.DOTALL):
            features.add(feature)

    depth = 0
    for line in source.splitlines():
        if re.match(r"^\s*group\s+", line) and depth > 1:
            features.add("nested-groups")
        depth += line.count("{") - line.count("}")
    return features


catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
entries = catalog["examples"]

ids = [entry["id"] for entry in entries]
sources = [entry["source"] for entry in entries]
if len(ids) != len(set(ids)):
    raise SystemExit("example catalog contains a duplicate id")
if len(sources) != len(set(sources)):
    raise SystemExit("example catalog contains a duplicate source")

actual_sources = sorted(path.name for path in EXAMPLES.glob("*.stack"))
if sorted(sources) != actual_sources:
    raise SystemExit("example catalog does not contain every .stack source exactly once")

providers = set()
features = set()
stages = set()
for entry in entries:
    source_path = EXAMPLES / entry["source"]
    if source_path.parent != EXAMPLES:
        raise SystemExit(f"{entry['id']} source escapes the examples directory")
    source = source_path.read_text(encoding="utf-8")
    if not source.startswith("stack 1.0\n\n") or not source.endswith("\n"):
        raise SystemExit(f"{entry['source']} must be a canonical Stack 1.0 text file")

    expected = entry["expected"]
    actual = {
        "nodes": count_declarations(source, "node"),
        "groups": count_declarations(source, "group"),
        "edges": count_declarations(source, "edge"),
    }
    for field, count in actual.items():
        if expected[field] != count:
            raise SystemExit(
                f"{entry['id']} expects {expected[field]} {field}, found {count}"
            )

    referenced_providers = set(re.findall(r'icon "([a-z][a-z0-9-]+):', source))
    if referenced_providers != set(entry["providers"]):
        raise SystemExit(
            f"{entry['id']} provider metadata does not match its icon identifiers"
        )
    if bool(referenced_providers) != ("provider-icons" in entry["features"]):
        raise SystemExit(f"{entry['id']} provider-icons feature metadata is inconsistent")

    represented = represented_features(source)
    if represented != set(entry["features"]):
        missing = sorted(represented - set(entry["features"]))
        extra = sorted(set(entry["features"]) - represented)
        raise SystemExit(
            f"{entry['id']} feature metadata mismatch: missing={missing}, extra={extra}"
        )

    providers.update(entry["providers"])
    features.update(entry["features"])
    stages.add(entry["learningStage"])

required_providers = {"aws", "gcp", "azure", "simple-icons"}
if providers != required_providers:
    raise SystemExit("example catalog does not cover every supported provider namespace")
if stages != {"starter", "intermediate", "advanced"}:
    raise SystemExit("example catalog does not cover every learning stage")

required_features = {
    "themes",
    "node-kinds",
    "node-details",
    "groups",
    "nested-groups",
    "layout-direction",
    "rank-constraints",
    "order-constraints",
    "edge-labels",
    "edge-kinds",
    "directed-edges",
    "bidirectional-edges",
    "association-edges",
    "provider-icons",
}
if features != required_features:
    missing = sorted(required_features - features)
    extra = sorted(features - required_features)
    raise SystemExit(f"example feature coverage mismatch: missing={missing}, extra={extra}")

print(
    f"Validated {len(entries)} Stack examples across {len(stages)} learning stages "
    f"and {len(providers)} provider namespaces."
)
