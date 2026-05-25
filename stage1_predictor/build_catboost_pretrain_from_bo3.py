from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .catboost_model import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, build_pair_features
from .collect_bo3_dataset import normalize_name
from .factor_snapshot import build_factor_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build CatBoost pretrain features from BO3 match/map rows")
    parser.add_argument("--matches", required=True, help="BO3 match rows CSV")
    parser.add_argument("--maps", required=True, help="BO3 map rows CSV")
    parser.add_argument("--feature-snapshot", required=True, help="Current Stage 1 factor snapshot for the 16 teams")
    parser.add_argument("--raw-detail-dir", default="data/raw/bo3/match_details")
    parser.add_argument("--output", required=True, help="Featureized CatBoost pretrain CSV")
    parser.add_argument("--report", required=True, help="Markdown report")
    parser.add_argument("--sample-weight", type=float, default=0.30)
    parser.add_argument("--stage-vs-stage-weight", type=float, default=0.45)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    snapshot_rows = load_snapshot_rows(args.feature_snapshot)
    matches = load_match_index(args.matches)
    rows = build_pretrain_rows(
        map_rows=load_rows(args.maps),
        match_rows=matches,
        snapshot_rows=snapshot_rows,
        raw_detail_dir=Path(args.raw_detail_dir),
        sample_weight=args.sample_weight,
        stage_vs_stage_weight=args.stage_vs_stage_weight,
    )
    write_rows(args.output, rows)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(args.matches, args.maps, args.output, rows), encoding="utf-8")
    print(f"Wrote {len(rows)} BO3 CatBoost pretrain rows to {args.output}")
    return 0


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"CSV is empty: {path}")
    return rows


def load_snapshot_rows(path: str | Path) -> dict[str, dict[str, str]]:
    rows = load_rows(path)
    if "factor_score" not in rows[0]:
        rows = build_factor_rows(rows)
    return {normalize_name(row["team"]): row for row in rows}


def load_match_index(path: str | Path) -> dict[str, dict[str, str]]:
    rows = load_rows(path)
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        output[row["slug"]] = row
        output[row["match_id"]] = row
    return output


def build_pretrain_rows(
    *,
    map_rows: list[dict[str, str]],
    match_rows: dict[str, dict[str, str]],
    snapshot_rows: dict[str, dict[str, str]],
    raw_detail_dir: Path,
    sample_weight: float,
    stage_vs_stage_weight: float,
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    skipped = 0
    for map_row in map_rows:
        if map_row.get("status") != "finished":
            continue
        match = match_rows.get(map_row.get("slug", "")) or match_rows.get(map_row.get("match_id", ""))
        if not match:
            skipped += 1
            continue
        team1 = map_row.get("team1", "")
        team2 = map_row.get("team2", "")
        winner = map_row.get("winner", "")
        target1 = map_target(team1, team2, winner)
        if target1 is None:
            skipped += 1
            continue
        left = feature_row_for_team(team1, match, snapshot_rows)
        right = feature_row_for_team(team2, match, snapshot_rows)
        if not left or not right:
            skipped += 1
            continue
        weight = stage_vs_stage_weight if is_stage_team(left, snapshot_rows) and is_stage_team(right, snapshot_rows) else sample_weight
        output.append(build_row(left, right, map_row, match, raw_detail_dir, target1, weight))
        output.append(build_row(right, left, map_row, match, raw_detail_dir, 1 - target1, weight))
    if not output:
        raise ValueError("No BO3 map rows could be converted into CatBoost pretrain rows")
    if skipped:
        for row in output:
            row.setdefault("_skipped_rows", str(skipped))
    return output


def map_target(team1: str, team2: str, winner: str) -> int | None:
    winner_key = normalize_name(winner)
    if winner_key == normalize_name(team1):
        return 1
    if winner_key == normalize_name(team2):
        return 0
    return None


def feature_row_for_team(team: str, match: dict[str, str], snapshot_rows: dict[str, dict[str, str]]) -> dict[str, str]:
    key = normalize_name(team)
    if key in snapshot_rows:
        return dict(snapshot_rows[key])
    side = side_for_team(team, match)
    rank = match.get(f"{side}_vrs_rank", "") or match.get(f"{side}_rank_bo3", "") or "100"
    points = match.get(f"{side}_vrs_points", "") or fallback_points(rank)
    return {
        "event_id": "bo3_last4months_pretrain",
        "team": team,
        "seed": rank,
        "score": points,
        "vrs_points": points,
        "region": "",
        "hltv_rating3": "1.00",
        "hltv_kd": "1.00",
        "hltv_maps": "0",
        "base_strength_factor": "50",
        "seed_path_factor": "50",
        "hltv_rating_factor": "50",
        "firepower_factor": "50",
        "map_pool_depth_factor": "50",
        "sample_confidence_factor": "35",
        "opponent_quality_proxy_factor": "50",
        "roster_data_factor": "35",
        "overall_factor_rating": "50",
        "format_type": "bo3_last4months_match_map",
        "round_system": "match_map_pretrain",
    }


def side_for_team(team: str, match: dict[str, str]) -> str:
    if normalize_name(team) == normalize_name(match.get("team1", "")):
        return "team1"
    return "team2"


def fallback_points(rank: str) -> str:
    try:
        rank_value = max(1, int(float(rank)))
    except ValueError:
        rank_value = 100
    return str(max(800, 1700 - rank_value * 6))


def is_stage_team(row: dict[str, str], snapshot_rows: dict[str, dict[str, str]]) -> bool:
    return normalize_name(row.get("team", "")) in snapshot_rows


def build_row(
    left: dict[str, str],
    right: dict[str, str],
    map_row: dict[str, str],
    match: dict[str, str],
    raw_detail_dir: Path,
    target: int,
    sample_weight: float,
) -> dict[str, str]:
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
            "sample_weight": f"{sample_weight:.3f}",
            "source_url": match["source_url"],
            "cache_path": str(raw_detail_dir / f"{match['slug']}.json"),
            "match_date": match.get("start_date", "")[:10],
            "map": map_row.get("map_name", ""),
            "best_of": f"BO{match.get('bo_type', '')}",
            "veto_sequence": map_row.get("veto_sequence", ""),
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
        writer.writerows([{name: row.get(name, "") for name in fieldnames} for row in rows])


def render_report(matches_path: str, maps_path: str, output_path: str, rows: list[dict[str, str]]) -> str:
    teams = sorted({row["team"] for row in rows})
    veto_rows = sum(1 for row in rows if row.get("veto_sequence"))
    lines = [
        "# BO3 CatBoost Pretrain Dataset",
        "",
        f"- Matches input: `{matches_path}`",
        f"- Maps input: `{maps_path}`",
        f"- Output: `{output_path}`",
        f"- Featureized rows: `{len(rows)}`",
        f"- Rows with veto sequence: `{veto_rows}`",
        f"- Teams with directed rows: `{len(teams)}`",
        "",
        "## Notes",
        "",
        "Rows are directed pairwise map examples built from BO3.gg match/map results. Current Cologne Stage 1 teams use the factor snapshot; VRS Top 100 opponents outside the snapshot use conservative VRS/BO3 rank defaults so the 16 teams can still learn from broader recent opposition.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
