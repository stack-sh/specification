#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "conformance" / "language-intelligence"
REQUIRED_FILES = {"source.stack", "fixture.json"}
FEATURES = {"diagnostics", "completion", "hover", "documentSymbols", "format"}


def source_position(source: bytes, byte_offset: int) -> tuple[int, int]:
    if byte_offset < 0 or byte_offset > len(source):
        raise ValueError(f"byte offset {byte_offset} is outside the source")
    try:
        source[:byte_offset].decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"byte offset {byte_offset} is not a UTF-8 scalar boundary") from error

    line = 1
    column = 1
    cursor = 0
    while cursor < byte_offset:
        if source[cursor : cursor + 2] == b"\r\n":
            if cursor + 1 == byte_offset:
                raise ValueError(f"byte offset {byte_offset} splits a CRLF sequence")
            line += 1
            column = 1
            cursor += 2
            continue

        first = source[cursor]
        width = 1
        if first >= 0xF0:
            width = 4
        elif first >= 0xE0:
            width = 3
        elif first >= 0xC0:
            width = 2
        character = source[cursor : cursor + width].decode("utf-8")
        if character == "\n":
            line += 1
            column = 1
        else:
            column += 1
        cursor += width
    return line, column


def validate_position(source: bytes, position: dict, context: str) -> int:
    byte_offset = position["byteOffset"]
    line, column = source_position(source, byte_offset)
    if position["line"] != line or position["column"] != column:
        raise ValueError(
            f"{context}: byte offset {byte_offset} resolves to {line}:{column}, "
            f"not {position['line']}:{position['column']}"
        )
    return byte_offset


def validate_range(source: bytes, source_range: dict, context: str) -> tuple[int, int]:
    start = validate_position(source, source_range["start"], f"{context}.start")
    end = validate_position(source, source_range["end"], f"{context}.end")
    if start > end:
        raise ValueError(f"{context}: range start follows range end")
    return start, end


def walk_ranges(source: bytes, value: object, context: str) -> None:
    if isinstance(value, list):
        for index, item in enumerate(value):
            walk_ranges(source, item, f"{context}[{index}]")
        return
    if not isinstance(value, dict):
        return
    if set(value) == {"start", "end"} and all(
        isinstance(value[key], dict) and "byteOffset" in value[key]
        for key in ("start", "end")
    ):
        validate_range(source, value, context)
        return
    if {"byteOffset", "line", "column"}.issubset(value):
        validate_position(source, value, context)
        return
    for key, item in value.items():
        walk_ranges(source, item, f"{context}.{key}")


def validate_completion(source: bytes, operation: dict, context: str) -> None:
    request = operation["request"]
    response = operation["response"]
    cursor = validate_position(source, request["position"], f"{context}.request.position")

    icon_ids = [entry["id"] for entry in request["completionCatalog"]["icons"]]
    if len(icon_ids) != len(set(icon_ids)):
        raise ValueError(f"{context}: completion catalog repeats an icon id")

    items = response["items"]
    ordering = [(item["sortText"].encode(), item["label"].encode()) for item in items]
    if ordering != sorted(ordering):
        raise ValueError(f"{context}: completion items are not in deterministic order")

    identities = set()
    for index, item in enumerate(items):
        start, end = validate_range(source, item["edit"]["range"], f"{context}.items[{index}].edit.range")
        if not start <= cursor <= end:
            raise ValueError(f"{context}: completion edit does not contain the request position")
        identity = (item["label"], start, end, item["edit"]["newText"])
        if identity in identities:
            raise ValueError(f"{context}: completion response contains a duplicate item")
        identities.add(identity)
        if item["kind"] == "icon" and item["edit"]["newText"] not in icon_ids:
            raise ValueError(f"{context}: completion invented an icon outside the request catalog")


def validate_hover(source: bytes, operation: dict, context: str) -> None:
    cursor = validate_position(source, operation["request"]["position"], f"{context}.request.position")
    hover = operation["response"]["hover"]
    if hover is None:
        return
    start, end = validate_range(source, hover["range"], f"{context}.response.hover.range")
    if not start <= cursor <= end:
        raise ValueError(f"{context}: hover range does not contain the request position")


def validate_symbols(source: bytes, symbols: list, parent: tuple[int, int] | None, context: str) -> None:
    starts = []
    for index, symbol in enumerate(symbols):
        symbol_context = f"{context}[{index}]"
        start, end = validate_range(source, symbol["range"], f"{symbol_context}.range")
        selection_start, selection_end = validate_range(
            source, symbol["selectionRange"], f"{symbol_context}.selectionRange"
        )
        if not start <= selection_start <= selection_end <= end:
            raise ValueError(f"{symbol_context}: selection range escapes the symbol")
        if parent is not None and not parent[0] <= start <= end <= parent[1]:
            raise ValueError(f"{symbol_context}: child range escapes its parent")
        starts.append(start)
        validate_symbols(source, symbol["children"], (start, end), f"{symbol_context}.children")
    if starts != sorted(starts):
        raise ValueError(f"{context}: symbols are not in source order")


def validate_format(source: bytes, edits: list, context: str) -> None:
    ranges = []
    for index, edit in enumerate(edits):
        start, end = validate_range(source, edit["range"], f"{context}.edits[{index}].range")
        ranges.append((start, end, edit["newText"].encode("utf-8")))
    if ranges != sorted(ranges, key=lambda item: (item[0], item[1])):
        raise ValueError(f"{context}: format edits are not ordered by source range")
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise ValueError(f"{context}: format edits overlap")

    formatted = source
    for start, end, new_text in reversed(ranges):
        formatted = formatted[:start] + new_text + formatted[end:]
    formatted.decode("utf-8")
    if ranges and (not formatted.endswith(b"\n") or formatted.endswith(b"\n\n") or b"\r" in formatted):
        raise ValueError(f"{context}: canonical fixture output must end with exactly one LF")


def main() -> None:
    cases = sorted(path for path in FIXTURES.iterdir() if path.is_dir())
    if not cases:
        raise ValueError(f"{FIXTURES}: no language-intelligence cases found")

    covered_features = set()
    has_partial_completion = False
    has_catalog_completion = False
    has_hover = False
    has_format_edit = False

    for case in cases:
        actual_files = {path.name for path in case.iterdir() if path.is_file()}
        if actual_files != REQUIRED_FILES:
            raise ValueError(
                f"{case}: expected files {sorted(REQUIRED_FILES)}, found {sorted(actual_files)}"
            )

        source = (case / "source.stack").read_bytes()
        if source.startswith(b"\xef\xbb\xbf"):
            raise ValueError(f"{case}: source must not contain a byte order mark")
        source.decode("utf-8")
        fixture = json.loads((case / "fixture.json").read_text(encoding="utf-8"))
        operation_ids = [operation["id"] for operation in fixture["operations"]]
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError(f"{case}: operation ids must be unique")

        for operation in fixture["operations"]:
            context = f"{case.name}/{operation['id']}"
            request = operation["request"]
            response = operation["response"]
            for field in ("schemaVersion", "documentVersion", "feature"):
                if request[field] != response[field]:
                    raise ValueError(f"{context}: response does not echo request {field}")
            covered_features.add(request["feature"])
            walk_ranges(source, operation, context)

            if request["feature"] == "completion":
                validate_completion(source, operation, context)
                has_catalog_completion = has_catalog_completion or bool(
                    request["completionCatalog"]["icons"]
                )
                has_partial_completion = has_partial_completion or bool(response["diagnostics"])
            elif request["feature"] == "hover":
                validate_hover(source, operation, context)
                has_hover = has_hover or response["hover"] is not None
            elif request["feature"] == "documentSymbols":
                validate_symbols(source, response["symbols"], None, f"{context}.response.symbols")
            elif request["feature"] == "format":
                validate_format(source, response["edits"], f"{context}.response")
                has_format_edit = has_format_edit or bool(response["edits"])

    if covered_features != FEATURES:
        raise ValueError(
            f"language-intelligence fixtures cover {sorted(covered_features)}, expected {sorted(FEATURES)}"
        )
    if not has_partial_completion:
        raise ValueError("fixtures must include completion alongside an invalid-document diagnostic")
    if not has_catalog_completion:
        raise ValueError("fixtures must include caller-owned icon completion")
    if not has_hover:
        raise ValueError("fixtures must include a resolved hover")
    if not has_format_edit:
        raise ValueError("fixtures must include a canonical format edit")

    print(
        f"Validated {len(cases)} language-intelligence cases across "
        f"{len(covered_features)} features."
    )


if __name__ == "__main__":
    main()
