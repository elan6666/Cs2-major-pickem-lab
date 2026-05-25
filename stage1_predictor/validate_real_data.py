from __future__ import annotations

import argparse
from pathlib import Path

from .data_provenance import (
    combine_results,
    validate_fetch_attempt_report,
    validate_pretrain_csv,
    validate_source_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate that model data is backed by real HLTV fetch provenance")
    parser.add_argument("--fetch-attempt-json", action="append", default=[], help="HLTV fetch-attempt JSON report")
    parser.add_argument("--source-csv", action="append", default=[], help="CSV with source_url fields")
    parser.add_argument("--map-stats-csv", action="append", default=[], help="Map stats CSV with source field")
    parser.add_argument("--pretrain-csv", action="append", default=[], help="CatBoost pretrain CSV with source_url/cache_path")
    parser.add_argument("--allow-blocked-fetch", action="store_true", help="Do not require fetch attempts to be status=200 and unblocked")
    parser.add_argument("--report", help="Optional Markdown report path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = []
    for path in args.fetch_attempt_json:
        results.append(validate_fetch_attempt_report(path, require_success=not args.allow_blocked_fetch))
    for path in args.source_csv:
        results.append(validate_source_csv(path, ("source_url",)))
    for path in args.map_stats_csv:
        results.append(validate_source_csv(path, ("source",)))
    for path in args.pretrain_csv:
        results.append(validate_pretrain_csv(path))
    result = combine_results(results)
    report = render_report(result)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(report, encoding="utf-8")
    print(report)
    return 0 if result.ok else 2


def render_report(result) -> str:
    lines = ["# Real Data Provenance Validation", ""]
    verdict = "PASS" if result.ok else "FAIL"
    lines.append(f"- Verdict: `{verdict}`")
    if result.errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result.errors)
    if result.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result.warnings)
    if result.ok:
        lines.extend(["", "All checked sources have acceptable HLTV provenance."])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
