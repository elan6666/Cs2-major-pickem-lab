from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .catboost_model import VRS_TIER_FEATURE_COLUMNS
from .collect_bo3_dataset import normalize_name
from .factor_snapshot import build_factor_rows
from .map_veto import DEFAULT_MAP_POOL, normalize_map_name


CUMULATIVE_TIERS = (10, 20, 30, 40, 50, 70, 100)
BUCKETS = ((1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 70), (71, 100))
PRIOR_WEIGHT = 6.0


@dataclass(frozen=True)
class Observation:
    team: str
    map_name: str
    opponent_rank: int
    won: bool
    round_margin: int
    scoreline_quality: float
    overtime: bool
    close_loss: bool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build VRS-tier opponent-quality map features with CS2 scoreline quality")
    parser.add_argument("--matches", required=True, help="BO3 match rows with 2026-05-04 VRS rank/points columns")
    parser.add_argument("--maps", required=True, help="BO3 map result rows with winner_score/loser_score")
    parser.add_argument("--feature-snapshot", required=True, help="Current event feature snapshot to augment")
    parser.add_argument("--base-map-stats", help="Optional existing map_veto CSV whose pick/ban rates should be preserved")
    parser.add_argument("--team-map-output", required=True, help="Per-team-per-map VRS tier feature CSV")
    parser.add_argument("--snapshot-output", required=True, help="Augmented event feature snapshot")
    parser.add_argument("--map-stats-output", required=True, help="map_veto-compatible scoreline-adjusted map stats CSV")
    parser.add_argument("--report", required=True, help="Markdown report")
    parser.add_argument("--map-pool", default=",".join(DEFAULT_MAP_POOL), help="Comma-separated active map pool")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    match_rows = load_rows(args.matches)
    map_rows = load_rows(args.maps)
    snapshot_rows = load_snapshot_rows(args.feature_snapshot)
    map_pool = tuple(normalize_map_name(value) for value in args.map_pool.split(",") if value.strip())
    observations = build_observations(map_rows, build_match_index(match_rows))
    team_map_rows = build_team_map_rows(observations)
    write_rows(args.team_map_output, team_map_rows)
    augmented_snapshot = augment_snapshot_rows(snapshot_rows, team_map_rows, map_pool)
    write_rows(args.snapshot_output, augmented_snapshot)
    base_map_stats = load_base_map_stats(args.base_map_stats) if args.base_map_stats else {}
    map_stats_rows = build_adjusted_map_stats_rows(team_map_rows, base_map_stats)
    write_rows(args.map_stats_output, map_stats_rows)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        render_report(args.matches, args.maps, args.team_map_output, args.snapshot_output, args.map_stats_output, observations, team_map_rows),
        encoding="utf-8",
    )
    print(f"Wrote {len(team_map_rows)} VRS-tier team-map rows to {args.team_map_output}")
    print(f"Wrote {len(augmented_snapshot)} augmented snapshot rows to {args.snapshot_output}")
    print(f"Wrote {len(map_stats_rows)} scoreline-adjusted map-stat rows to {args.map_stats_output}")
    return 0


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"CSV is empty: {path}")
    return rows


def load_snapshot_rows(path: str | Path) -> list[dict[str, str]]:
    rows = load_rows(path)
    if "factor_score" not in rows[0]:
        rows = build_factor_rows(rows)
    return rows


def load_base_map_stats(path: str | Path) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (normalize_name(row["team"]), normalize_map_name(row["map"])): row
        for row in load_rows(path)
        if row.get("team") and row.get("map")
    }


def build_match_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        if row.get("slug"):
            output[row["slug"]] = row
        if row.get("match_id"):
            output[row["match_id"]] = row
    return output


def build_observations(map_rows: list[dict[str, str]], matches: dict[str, dict[str, str]]) -> list[Observation]:
    observations: list[Observation] = []
    for row in map_rows:
        if row.get("status") != "finished":
            continue
        match = matches.get(row.get("slug", "")) or matches.get(row.get("match_id", ""))
        if not match:
            continue
        team1 = row.get("team1", "")
        team2 = row.get("team2", "")
        winner = normalize_name(row.get("winner", ""))
        if winner not in {normalize_name(team1), normalize_name(team2)}:
            continue
        winner_score = int_number(row.get("winner_score"))
        loser_score = int_number(row.get("loser_score"))
        if winner_score <= 0:
            continue
        for team, opponent in ((team1, team2), (team2, team1)):
            won = normalize_name(team) == winner
            team_score = winner_score if won else loser_score
            opponent_score = loser_score if won else winner_score
            margin = team_score - opponent_score
            observations.append(
                Observation(
                    team=canonical_team_name(team, match),
                    map_name=normalize_map_name(row.get("map_name", "")),
                    opponent_rank=opponent_vrs_rank(team, opponent, match),
                    won=won,
                    round_margin=margin,
                    scoreline_quality=scoreline_quality(team_score, opponent_score),
                    overtime=is_overtime_score(team_score, opponent_score),
                    close_loss=(not won) and is_close_score(team_score, opponent_score),
                )
            )
    return observations


def canonical_team_name(team: str, match: dict[str, str]) -> str:
    key = normalize_name(team)
    for side in ("team1", "team2"):
        if normalize_name(match.get(side, "")) == key:
            return match.get(side, team)
    return team


def opponent_vrs_rank(team: str, opponent: str, match: dict[str, str]) -> int:
    team_key = normalize_name(team)
    opponent_side = "team2" if normalize_name(match.get("team1", "")) == team_key else "team1"
    if normalize_name(match.get(opponent_side, "")) != normalize_name(opponent):
        opponent_side = "team1" if opponent_side == "team2" else "team2"
    return max(1, int_number(match.get(f"{opponent_side}_vrs_rank") or match.get(f"{opponent_side}_rank_bo3"), default=100))


def scoreline_quality(team_score: int, opponent_score: int) -> float:
    margin = team_score - opponent_score
    if is_overtime_score(team_score, opponent_score):
        target = overtime_target(max(team_score, opponent_score))
        return clamp(margin / max(16.0, float(target)), -0.45, 0.45)
    return clamp(margin / 10.0, -1.0, 1.0)


def is_overtime_score(team_score: int, opponent_score: int) -> bool:
    return max(team_score, opponent_score) >= 16 or (team_score + opponent_score) > 24


def overtime_target(winner_score: int) -> int:
    if winner_score <= 13:
        return 13
    return 16 + max(0, math.ceil((winner_score - 16) / 3)) * 3


def is_close_score(team_score: int, opponent_score: int) -> bool:
    return abs(team_score - opponent_score) <= 2 or is_overtime_score(team_score, opponent_score)


def build_team_map_rows(observations: list[Observation]) -> list[dict[str, str]]:
    by_team_map: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    by_map: dict[str, list[Observation]] = defaultdict(list)
    for observation in observations:
        by_team_map[(observation.team, observation.map_name)].append(observation)
        by_map[observation.map_name].append(observation)

    rows: list[dict[str, str]] = []
    for (team, map_name), team_map_observations in sorted(by_team_map.items()):
        global_map_observations = by_map[map_name]
        base = aggregate(team_map_observations, global_map_observations)
        row = {
            "team": team,
            "map": map_name,
            **format_aggregate("", base),
            "vrs_tier_map_strength": f"{adjusted_strength(base):.2f}",
            "vrs_tier_map_smoothed_win_rate": f"{base['smoothed_win_rate']:.2f}",
            "vrs_tier_map_sample_log": f"{math.log1p(base['maps']):.6f}",
            "vrs_tier_map_quality": f"{base['avg_scoreline_quality']:.6f}",
            "vrs_tier_map_round_margin": f"{base['avg_round_margin']:.6f}",
            "vrs_tier_map_overtime_rate": f"{rate(base['overtime_count'], base['maps']):.6f}",
            "vrs_tier_map_close_loss_rate": f"{rate(base['close_loss_count'], base['maps']):.6f}",
        }
        for threshold in CUMULATIVE_TIERS:
            tier_observations = [item for item in team_map_observations if item.opponent_rank <= threshold]
            tier = aggregate(tier_observations, global_map_observations, prior_observations=team_map_observations)
            prefix = f"vrs_top{threshold}_"
            row.update(format_aggregate(prefix, tier))
            row[f"vrs_top{threshold}_map_smoothed_win_rate"] = f"{tier['smoothed_win_rate']:.2f}"
            row[f"vrs_top{threshold}_map_quality"] = f"{tier['avg_scoreline_quality']:.6f}"
            row[f"vrs_top{threshold}_map_sample_log"] = f"{math.log1p(tier['maps']):.6f}"
        for lower, upper in BUCKETS:
            bucket_observations = [item for item in team_map_observations if lower <= item.opponent_rank <= upper]
            bucket = aggregate(bucket_observations, global_map_observations, prior_observations=team_map_observations)
            row.update(format_aggregate(f"vrs_bucket_{lower}_{upper}_", bucket))
        rows.append(row)
    return rows


def aggregate(
    observations: list[Observation],
    global_observations: list[Observation],
    prior_observations: list[Observation] | None = None,
) -> dict[str, float]:
    maps = len(observations)
    wins = sum(1 for item in observations if item.won)
    raw_win_rate = wins / maps * 100.0 if maps else 50.0
    team_prior = prior_observations if prior_observations is not None else observations
    team_prior_rate = win_rate(team_prior)
    global_prior_rate = win_rate(global_observations)
    prior_rate = 0.70 * team_prior_rate + 0.30 * global_prior_rate
    smoothed = (wins + prior_rate * PRIOR_WEIGHT) / (maps + PRIOR_WEIGHT) * 100.0
    quality = average([item.scoreline_quality for item in observations], average([item.scoreline_quality for item in team_prior], 0.0))
    margin = average([item.round_margin for item in observations], average([item.round_margin for item in team_prior], 0.0))
    return {
        "maps": float(maps),
        "wins": float(wins),
        "raw_win_rate": raw_win_rate,
        "smoothed_win_rate": smoothed,
        "avg_round_margin": margin,
        "avg_scoreline_quality": quality,
        "overtime_count": float(sum(1 for item in observations if item.overtime)),
        "close_loss_count": float(sum(1 for item in observations if item.close_loss)),
    }


def format_aggregate(prefix: str, values: dict[str, float]) -> dict[str, str]:
    return {
        f"{prefix}maps": f"{int(values['maps'])}",
        f"{prefix}wins": f"{int(values['wins'])}",
        f"{prefix}raw_win_rate": f"{values['raw_win_rate']:.2f}",
        f"{prefix}smoothed_win_rate": f"{values['smoothed_win_rate']:.2f}",
        f"{prefix}avg_round_margin": f"{values['avg_round_margin']:.6f}",
        f"{prefix}avg_scoreline_quality": f"{values['avg_scoreline_quality']:.6f}",
        f"{prefix}overtime_count": f"{int(values['overtime_count'])}",
        f"{prefix}close_loss_count": f"{int(values['close_loss_count'])}",
    }


def augment_snapshot_rows(snapshot_rows: list[dict[str, str]], team_map_rows: list[dict[str, str]], map_pool: tuple[str, ...]) -> list[dict[str, str]]:
    by_team_map = {(normalize_name(row["team"]), normalize_map_name(row["map"])): row for row in team_map_rows}
    output: list[dict[str, str]] = []
    for row in snapshot_rows:
        enriched = dict(row)
        team_key = normalize_name(row["team"])
        selected = [by_team_map.get((team_key, map_name)) for map_name in map_pool]
        aggregate_features = aggregate_feature_rows([item for item in selected if item])
        for column in VRS_TIER_FEATURE_COLUMNS:
            enriched[column] = f"{aggregate_features.get(column, default_feature_value(column)):.6f}"
        output.append(enriched)
    return output


def aggregate_feature_rows(rows: list[dict[str, str]]) -> dict[str, float]:
    if not rows:
        return {}
    output: dict[str, float] = {}
    for column in VRS_TIER_FEATURE_COLUMNS:
        default = default_feature_value(column)
        output[column] = average([float_number(row.get(column), default) for row in rows], default)
    return output


def build_adjusted_map_stats_rows(
    team_map_rows: list[dict[str, str]],
    base_map_stats: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in team_map_rows:
        maps = int_number(row.get("maps"))
        strength = float_number(row.get("vrs_tier_map_strength"), 50.0)
        base = base_map_stats.get((normalize_name(row["team"]), normalize_map_name(row["map"])), {})
        output.append(
            {
                "team": row["team"],
                "map": row["map"],
                "win_rate": f"{strength:.2f}",
                "maps_played": str(maps),
                "pick_rate": base.get("pick_rate", "0.00"),
                "ban_rate": base.get("ban_rate", "0.00"),
                "pistol_win_rate": base.get("pistol_win_rate", ""),
                "first_kill_round_win_rate": base.get("first_kill_round_win_rate", ""),
                "first_death_round_win_rate": base.get("first_death_round_win_rate", ""),
                "source": "BO3 map results adjusted by VRS tier and CS2 scoreline quality",
            }
        )
    return output


def adjusted_strength(values: dict[str, float]) -> float:
    return clamp(values["smoothed_win_rate"] + values["avg_scoreline_quality"] * 8.0, 5.0, 95.0)


def win_rate(observations: list[Observation]) -> float:
    if not observations:
        return 0.5
    return sum(1 for item in observations if item.won) / len(observations)


def average(values: list[float], default: float) -> float:
    return sum(values) / len(values) if values else default


def rate(value: float, total: float) -> float:
    return value / total if total else 0.0


def clamp(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


def int_number(value: str | None, default: int = 0) -> int:
    if value is None or str(value).strip() == "":
        return default
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return default


def float_number(value: str | None, default: float = 0.0) -> float:
    if value is None or str(value).strip() == "":
        return default
    try:
        return float(str(value).strip())
    except ValueError:
        return default


def default_feature_value(column: str) -> float:
    if column.endswith("_win_rate") or column.endswith("_strength"):
        return 50.0
    return 0.0


def write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for name in row:
            if name not in fieldnames:
                fieldnames.append(name)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{name: row.get(name, "") for name in fieldnames} for row in rows])


def render_report(
    matches_path: str,
    maps_path: str,
    team_map_output: str,
    snapshot_output: str,
    map_stats_output: str,
    observations: list[Observation],
    team_map_rows: list[dict[str, str]],
) -> str:
    teams = sorted({row["team"] for row in team_map_rows})
    maps = sorted({row["map"] for row in team_map_rows})
    overtime = sum(1 for item in observations if item.overtime)
    close_losses = sum(1 for item in observations if item.close_loss)
    return "\n".join(
        [
            "# VRS Tier Scoreline Map Features",
            "",
            f"- Matches input: `{matches_path}`",
            f"- Maps input: `{maps_path}`",
            f"- Team-map output: `{team_map_output}`",
            f"- Augmented snapshot: `{snapshot_output}`",
            f"- Scoreline-adjusted map stats: `{map_stats_output}`",
            f"- Team-map rows: `{len(team_map_rows)}`",
            f"- Teams: `{len(teams)}`",
            f"- Maps: `{len(maps)}`",
            f"- Directed map observations: `{len(observations)}`",
            f"- Overtime observations: `{overtime}`",
            f"- Close-loss observations: `{close_losses}`",
            "",
            "## Feature Design",
            "",
            "- Cumulative tiers: VRS top 10/20/30/40/50/70/100.",
            "- Diagnostic buckets: VRS 1-10, 11-20, 21-30, 31-40, 41-50, 51-70, 71-100.",
            "- Smoothed win rates use Bayesian shrinkage toward a blend of team-map baseline and global map baseline.",
            "- Scoreline quality is MR12/overtime aware: regulation margins scale strongly, overtime margins stay close to zero.",
        ]
    ) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
