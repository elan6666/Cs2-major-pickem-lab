from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .catboost_model import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, build_pair_features, parse_target
from .factor_snapshot import build_factor_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build CatBoost pretrain features from real HLTV team match rows")
    parser.add_argument("--matches", required=True, help="Raw HLTV match rows CSV")
    parser.add_argument("--feature-snapshot", required=True, help="Stage team factor snapshot")
    parser.add_argument("--output", required=True, help="Featureized pretrain CSV")
    parser.add_argument("--report", required=True, help="Markdown report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    snapshot_rows = load_snapshot_rows(args.feature_snapshot)
    rows = build_pretrain_rows(load_match_rows(args.matches), snapshot_rows)
    write_rows(args.output, rows)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(args.matches, args.output, rows), encoding="utf-8")
    print(f"Wrote {len(rows)} CatBoost pretrain rows to {args.output}")
    return 0


def load_snapshot_rows(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Snapshot is empty: {path}")
    if "factor_score" not in rows[0]:
        rows = build_factor_rows(rows)
    return {row["team"]: row for row in rows}


def load_match_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Match CSV is empty: {path}")
    return rows


def build_pretrain_rows(match_rows: list[dict[str, str]], snapshot_rows: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for match in match_rows:
        team = match["team"]
        opponent = match["opponent"]
        if team not in snapshot_rows or opponent not in snapshot_rows:
            continue
        target = parse_target(match["target"])
        output.append(build_row(snapshot_rows[team], snapshot_rows[opponent], match, target))
        reverse_match = dict(match)
        reverse_match["team"], reverse_match["opponent"] = opponent, team
        reverse_match["score_for"], reverse_match["score_against"] = match["score_against"], match["score_for"]
        output.append(build_row(snapshot_rows[opponent], snapshot_rows[team], reverse_match, 1 - target))
    if not output:
        raise ValueError("No match rows overlapped with the feature snapshot teams")
    return output


def build_row(left: dict[str, str], right: dict[str, str], match: dict[str, str], target: int) -> dict[str, str]:
    features = build_pair_features(left, right)
    row: dict[str, str] = {}
    for name in FEATURES:
        value = features[name]
        if name in NUMERIC_FEATURES:
            row[name] = f"{float(value):.6f}"
        elif name in CATEGORICAL_FEATURES:
            row[name] = str(value)
        else:
            row[name] = str(value)
    row.update(
        {
            "target": str(target),
            "sample_weight": match.get("sample_weight", "1.0") or "1.0",
            "source_url": match["source_url"],
            "cache_path": match["cache_path"],
            "match_date": match["match_date"],
            "map": match["map"],
            "best_of": match.get("best_of", ""),
            "veto_sequence": match.get("veto_sequence", ""),
        }
    )
    return row


def write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [*FEATURES, "target", "sample_weight", "source_url", "cache_path", "match_date", "map", "best_of", "veto_sequence"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_report(input_path: str, output_path: str, rows: list[dict[str, str]]) -> str:
    teams = sorted({row["team"] for row in rows})
    sources = sorted({row["source_url"] for row in rows})
    lines = [
        "# HLTV CatBoost Pretrain Dataset",
        "",
        f"- Input: `{input_path}`",
        f"- Output: `{output_path}`",
        f"- Featureized rows: {len(rows)}",
        f"- Teams with rows: {', '.join(teams)}",
        "",
        "## Sources",
        "",
    ]
    lines.extend(f"- `{source}`" for source in sources)
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "Rows were extracted from official HLTV team match pages opened through the web tool and cached as local source snippets. Only rows where both teams are in the Stage 1 snapshot are converted into CatBoost pairwise examples.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
