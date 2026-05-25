from __future__ import annotations

import argparse

from .snapshots import validate_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an event-stage feature snapshot for leakage risk")
    parser.add_argument("snapshot", help="Snapshot CSV path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_snapshot(args.snapshot)
    if result.ok:
        print(f"OK: {result.path} ({result.rows} rows)")
        return 0
    print(f"FAILED: {result.path} ({result.rows} rows)")
    for error in result.errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
