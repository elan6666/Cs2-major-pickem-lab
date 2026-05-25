from __future__ import annotations

import argparse
from pathlib import Path

from .playoffs import (
    load_playoff_teams,
    render_playoff_report,
    run_playoff_simulations,
    summarize_playoff_probabilities,
    write_playoff_csv,
    write_playoff_json,
)
from .reporting import write_markdown_report
from .swiss import SimulationConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CS2 Major Playoffs predictor")
    parser.add_argument("--teams", required=True, help="Path to 8-team playoff teams CSV")
    parser.add_argument("--simulations", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scale", type=float, default=120.0)
    parser.add_argument("--bo3-shrink", type=float, default=1.00)
    parser.add_argument("--final-best-of", type=int, default=3, choices=(3, 5))
    parser.add_argument("--report", help="Optional Markdown report path")
    parser.add_argument("--csv", help="Optional probability CSV output path")
    parser.add_argument("--json", help="Optional JSON summary output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    teams = load_playoff_teams(args.teams)
    config = SimulationConfig(scale=args.scale, bo1_shrink=args.bo3_shrink, bo3_shrink=args.bo3_shrink)
    outcomes = run_playoff_simulations(teams, args.simulations, args.seed, config, args.final_best_of)
    rows = summarize_playoff_probabilities(teams, outcomes)
    settings = {
        "teams": str(Path(args.teams)),
        "simulations": args.simulations,
        "seed": args.seed,
        "scale": args.scale,
        "bo3_shrink": args.bo3_shrink,
        "final_best_of": args.final_best_of,
    }
    report = render_playoff_report(rows, settings)
    if args.report:
        write_markdown_report(args.report, report)
    if args.csv:
        write_playoff_csv(args.csv, rows)
    if args.json:
        write_playoff_json(args.json, rows, settings)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
