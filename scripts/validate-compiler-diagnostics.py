import json
from pathlib import Path


REQUIRED_COMPILER_DIAGNOSTICS = {
    "STK1001",
    "STK1002",
    "STK1003",
    "STK2001",
    "STK2002",
    "STK2003",
    "STK3001",
    "STK3002",
    "STK3003",
    "STK3004",
    "STK3005",
    "STK3006",
    "STK3007",
    "STK3008",
    "STK3009",
    "STK3010",
    "STK3011",
    "STK3012",
    "STK3013",
    "STK3014",
    "STK4002",
    "STK4003",
}


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    observed = set()
    for path in sorted((root / "conformance").glob("*/*/expected.diagnostics.json")):
        document = json.loads(path.read_bytes())
        observed.update(diagnostic["code"] for diagnostic in document["diagnostics"])

    missing = sorted(REQUIRED_COMPILER_DIAGNOSTICS - observed)
    if missing:
        raise SystemExit(f"missing compiler diagnostic expectations: {', '.join(missing)}")

    invalid_utf8 = (root / "conformance/invalid/invalid-utf8/source.stack").read_bytes()
    try:
        invalid_utf8.decode("utf-8")
    except UnicodeDecodeError:
        pass
    else:
        raise SystemExit("invalid-utf8/source.stack must contain invalid UTF-8")
    if b"\r\n" not in invalid_utf8:
        raise SystemExit("invalid-utf8/source.stack must exercise CRLF positions")

    byte_order_mark = (root / "conformance/invalid/byte-order-mark/source.stack").read_bytes()
    if not byte_order_mark.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("byte-order-mark/source.stack must begin with a UTF-8 BOM")


if __name__ == "__main__":
    main()
