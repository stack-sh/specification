from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "conformance" / "formatter"
REQUIRED_FILES = {"input.stack", "expected.stack", "expected.ir.json"}


def decode_utf8(path: Path, data: bytes) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{path}: UTF-8 byte order mark is not allowed")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path}: source is not valid UTF-8") from error


def validate_expected(path: Path, data: bytes) -> None:
    decode_utf8(path, data)
    if b"\r" in data:
        raise ValueError(f"{path}: canonical output must use LF line endings")
    if not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise ValueError(f"{path}: canonical output must end with exactly one LF")


def main() -> None:
    cases = sorted(path for path in FIXTURES.iterdir() if path.is_dir())
    if not cases:
        raise ValueError(f"{FIXTURES}: no formatter cases found")

    has_crlf_input = False
    for case in cases:
        actual_files = {path.name for path in case.iterdir() if path.is_file()}
        if actual_files != REQUIRED_FILES:
            raise ValueError(
                f"{case}: expected files {sorted(REQUIRED_FILES)}, "
                f"found {sorted(actual_files)}"
            )

        input_data = (case / "input.stack").read_bytes()
        expected_data = (case / "expected.stack").read_bytes()
        decode_utf8(case / "input.stack", input_data)
        validate_expected(case / "expected.stack", expected_data)
        has_crlf_input = has_crlf_input or b"\r\n" in input_data

    if not has_crlf_input:
        raise ValueError(f"{FIXTURES}: at least one input must exercise CRLF normalization")


if __name__ == "__main__":
    main()
