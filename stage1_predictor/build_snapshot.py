from __future__ import annotations

import argparse

from .snapshots import build_snapshot_from_stage_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a leakage-safe event-stage feature snapshot")
    parser.add_argument("--teams", required=True, help="Input teams CSV")
    parser.add_argument("--config", required=True, help="Stage config JSON")
    parser.add_argument("--output", required=True, help="Output snapshot CSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_snapshot_from_stage_config(args.teams, args.config, args.output)
    print(f"Wrote snapshot to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
