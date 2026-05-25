from __future__ import annotations

import argparse

from .vrs import build_teams_from_stage_config, load_stage_config, write_teams_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Stage 1 teams CSV from a VRS-backed config")
    parser.add_argument("--config", required=True, help="Path to stage config JSON")
    parser.add_argument("--output", required=True, help="Output teams CSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_stage_config(args.config)
    teams = build_teams_from_stage_config(config)
    write_teams_csv(args.output, teams)
    print(f"Wrote {len(teams)} teams to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
