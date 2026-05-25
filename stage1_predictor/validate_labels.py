from __future__ import annotations

import argparse

from .labels import validate_labels


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 1 outcome labels")
    parser.add_argument("labels", nargs="+", help="Label CSV path(s)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    exit_code = 0
    for path in args.labels:
        result = validate_labels(path)
        if result.ok:
            print(f"OK: {result.path} ({result.rows} rows)")
            continue
        exit_code = 1
        print(f"FAILED: {result.path} ({result.rows} rows)")
        for error in result.errors:
            print(f"- {error}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
