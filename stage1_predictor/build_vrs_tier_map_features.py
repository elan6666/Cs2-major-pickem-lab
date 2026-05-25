from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .catboost_model import VRS_TIER_FEATURE_COLUMNS
from .collect_bo3_dataset import normalize_name
from .factor_snapshot import build_factor_rows
from .map_veto import DEFAULT_MAP_POOL, normalize_map_name
from .vrs import parse_vrs_markdown


CUMULATIVE_TIERS = (10, 20, 30, 40, 50, 70, 100)
BUCKETS = ((1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 70), (71, 100))
PRIOR_WEIGHT = 6.0


@dataclass(frozen=True)
class VrsSnapshot:
    snapshot_date: date
    ranks_by_team: dict[str, int]


@dataclass(frozen=True)
class VrsTimeline:
    snapshots: tuple[VrsSnapshot, ...]

    def rank_for(self, team: str, match_date: date | None) -> int | None:
        snapshot = self.snapshot_for(match_date)
        if snapshot is None:
            return None
        return snapshot.ranks_by_team.get(normalize_name(team))

    def snapshot_date_for(self, match_date: date | None) -> str:
        snapshot = self.snapshot_for(match_date)
        return snapshot.snapshot_date.isoformat() if snapshot else ""

    def snapshot_for(self, match_date: date | None) -> VrsSnapshot | None:
        if not self.snapshots:
            return None
        if match_date is None:
            return self.snapshots[-1]
        prior = [snapshot for snapshot in self.snapshots if snapshot.snapshot_date <= match_date]
        if prior:
            return prior[-1]
        return self.snapshots[0]


@dataclass(frozen=True)
class Observation:
    team: str
    map_name: str
    team_rank: int
    opponent_rank: int
    won: bool
    round_margin: int
    expected_margin_residual: float
    scoreline_quality: float
    overtime: bool
    close_loss: bool
    start_date: date | None
    vrs_snapshot_date: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build VRS-tier opponent-quality map features with CS2 scoreline quality")
    parser.add_argument("--matches", required=True, help="BO3 match rows with 2026-05-04 VRS rank/points columns")
    parser.add_argument("--maps", required=True, help="BO3 map result rows with winner_score/loser_score")
    parser.add_argument("--feature-snapshot", required=True, help="Current event feature snapshot to augment")
    parser.add_argument("--base-map-stats", help="Optional existing map_veto CSV whose pick/ban rates should be preserved")
    parser.add_argument("--vrs-standings-dir", help="Optional directory of Valve standings_global_YYYY_MM_DD.md snapshots for match-date VRS ranks")
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
    base_map_stats = load_base_map_stats(args.base_map_stats) if args.base_map_stats else {}
    vrs_timeline = load_vrs_timeline(args.vrs_standings_dir) if args.vrs_standings_dir else None
    observations = build_observations(map_rows, build_match_index(match_rows), vrs_timeline)
    team_map_rows = build_team_map_rows(observations, base_map_stats)
    write_rows(args.team_map_output, team_map_rows)
    augmented_snapshot = augment_snapshot_rows(snapshot_rows, team_map_rows, map_pool)
    write_rows(args.snapshot_output, augmented_snapshot)
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


def load_vrs_timeline(directory: str | Path) -> VrsTimeline:
    snapshots: list[VrsSnapshot] = []
    for path in sorted(Path(directory).glob("standings_global_*.md")):
        snapshot_date = parse_vrs_snapshot_date(path.name)
        if snapshot_date is None:
            continue
        standings = parse_vrs_markdown(path.read_text(encoding="utf-8"))
        ranks = {normalize_name(entry.team): entry.rank for entry in standings.values()}
        if ranks:
            snapshots.append(VrsSnapshot(snapshot_date=snapshot_date, ranks_by_team=ranks))
    if not snapshots:
        raise ValueError(f"No standings_global_YYYY_MM_DD.md snapshots found in {directory}")
    return VrsTimeline(tuple(sorted(snapshots, key=lambda item: item.snapshot_date)))


def parse_vrs_snapshot_date(name: str) -> date | None:
    marker = "standings_global_"
    if marker not in name:
        return None
    raw = name.split(marker, 1)[1].removesuffix(".md")
    try:
        return datetime.strptime(raw, "%Y_%m_%d").date()
    except ValueError:
        return None


def build_match_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        if row.get("slug"):
            output[row["slug"]] = row
        if row.get("match_id"):
            output[row["match_id"]] = row
    return output


def build_observations(
    map_rows: list[dict[str, str]],
    matches: dict[str, dict[str, str]],
    vrs_timeline: "VrsTimeline | None" = None,
) -> list[Observation]:
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
            match_date = parse_date(match.get("start_date", ""))
            team_rank, snapshot_date = vrs_rank(team, match, match_date, vrs_timeline)
            opponent_rank, _ = vrs_rank(opponent, match, match_date, vrs_timeline)
            observations.append(
                Observation(
                    team=canonical_team_name(team, match),
                    map_name=normalize_map_name(row.get("map_name", "")),
                    team_rank=team_rank,
                    opponent_rank=opponent_rank,
                    won=won,
                    round_margin=margin,
                    expected_margin_residual=margin - expected_round_margin(team_rank, opponent_rank),
                    scoreline_quality=scoreline_quality(team_score, opponent_score),
                    overtime=is_overtime_score(team_score, opponent_score),
                    close_loss=(not won) and is_close_score(team_score, opponent_score),
                    start_date=match_date,
                    vrs_snapshot_date=snapshot_date,
                )
            )
    return observations


def canonical_team_name(team: str, match: dict[str, str]) -> str:
    key = normalize_name(team)
    for side in ("team1", "team2"):
        if normalize_name(match.get(side, "")) == key:
            return match.get(side, team)
    return team


def vrs_rank(team: str, match: dict[str, str], match_date: date | None, vrs_timeline: "VrsTimeline | None") -> tuple[int, str]:
    if vrs_timeline is not None:
        rank = vrs_timeline.rank_for(team, match_date)
        if rank is not None:
            return rank, vrs_timeline.snapshot_date_for(match_date)
    side = side_for_match_team(team, match)
    rank = max(1, int_number(match.get(f"{side}_vrs_rank") or match.get(f"{side}_rank_bo3"), default=100))
    return rank, "match_row"


def side_for_match_team(team: str, match: dict[str, str]) -> str:
    team_key = normalize_name(team)
    if normalize_name(match.get("team1", "")) == team_key:
        return "team1"
    return "team2"


def expected_round_margin(team_rank: int, opponent_rank: int) -> float:
    return clamp((opponent_rank - team_rank) / 10.0, -8.0, 8.0)


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


def build_team_map_rows(
    observations: list[Observation],
    base_map_stats: dict[tuple[str, str], dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    base_map_stats = base_map_stats or {}
    by_team_map: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    by_map: dict[str, list[Observation]] = defaultdict(list)
    for observation in observations:
        by_team_map[(observation.team, observation.map_name)].append(observation)
        by_map[observation.map_name].append(observation)

    rows: list[dict[str, str]] = []
    for (team, map_name), team_map_observations in sorted(by_team_map.items()):
        global_map_observations = by_map[map_name]
        base = aggregate(team_map_observations, global_map_observations)
        base_veto = base_map_stats.get((normalize_name(team), normalize_map_name(map_name)), {})
        pick_rate = float_number(base_veto.get("pick_rate"), 0.0)
        ban_rate = float_number(base_veto.get("ban_rate"), 0.0)
        interaction = interaction_features(base, pick_rate, ban_rate)
        row = {
            "team": team,
            "map": map_name,
            **format_aggregate("", base),
            "vrs_tier_map_strength": f"{interaction['vrs_tier_map_strength']:.2f}",
            "vrs_tier_map_smoothed_win_rate": f"{base['smoothed_win_rate']:.2f}",
            "vrs_tier_map_sample_log": f"{math.log1p(base['maps']):.6f}",
            "vrs_tier_map_quality": f"{base['avg_scoreline_quality']:.6f}",
            "vrs_tier_map_round_margin": f"{base['avg_round_margin']:.6f}",
            "vrs_tier_map_overtime_rate": f"{rate(base['overtime_count'], base['maps']):.6f}",
            "vrs_tier_map_close_loss_rate": f"{rate(base['close_loss_count'], base['maps']):.6f}",
            **{name: f"{value:.6f}" for name, value in interaction.items() if name != "vrs_tier_map_strength"},
            "vrs_seed_volatility_rebound": "0.000000",
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
    residual = average([item.expected_margin_residual for item in observations], average([item.expected_margin_residual for item in team_prior], 0.0))
    confidence = sample_confidence(maps)
    opponent_strength = average([opponent_strength_score(item.opponent_rank) for item in observations], average([opponent_strength_score(item.opponent_rank) for item in team_prior], 0.5))
    adjusted_quality = average([opponent_adjusted_scoreline(item) for item in observations], average([opponent_adjusted_scoreline(item) for item in team_prior], 0.0))
    recent_quality = average([recency_weight(item) * opponent_strength_score(item.opponent_rank) * item.scoreline_quality for item in observations], 0.0)
    overtime_strong = average([1.0 for item in observations if item.overtime and item.opponent_rank <= 30], 0.0)
    close_vs_strong = average([1.0 for item in observations if item.close_loss and item.opponent_rank <= 30], 0.0)
    weak_close_penalty = average([weak_opponent_close_penalty(item) for item in observations], 0.0)
    volatility = standard_deviation([item.round_margin for item in observations])
    return {
        "maps": float(maps),
        "wins": float(wins),
        "raw_win_rate": raw_win_rate,
        "smoothed_win_rate": smoothed,
        "avg_round_margin": margin,
        "avg_expected_margin_residual": residual,
        "avg_scoreline_quality": quality,
        "overtime_count": float(sum(1 for item in observations if item.overtime)),
        "close_loss_count": float(sum(1 for item in observations if item.close_loss)),
        "sample_confidence": confidence,
        "avg_opponent_strength": opponent_strength,
        "opponent_adjusted_scoreline_quality": adjusted_quality,
        "recent_strong_opponent_score": recent_quality,
        "overtime_strong_opponent_signal": overtime_strong + close_vs_strong * 0.5,
        "weak_opponent_close_penalty": weak_close_penalty,
        "team_volatility": volatility,
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
        seed = float_number(row.get("seed"), 8.0)
        volatility = aggregate_features.get("vrs_team_volatility", 0.0)
        aggregate_features["vrs_seed_volatility_rebound"] = volatility * clamp((seed - 8.0) / 8.0, 0.0, 1.5)
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
        strength = float_number(row.get("vrs_map_veto_strength"), float_number(row.get("vrs_tier_map_strength"), 50.0))
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


def interaction_features(values: dict[str, float], pick_rate: float, ban_rate: float) -> dict[str, float]:
    confidence = values["sample_confidence"]
    win_edge = values["smoothed_win_rate"] - 50.0
    opponent_factor = 0.65 + values["avg_opponent_strength"] * 0.70
    opponent_quality_edge = win_edge * opponent_factor / 2.0
    win_sample_edge = win_edge * confidence
    scoreline_sample = values["opponent_adjusted_scoreline_quality"] * confidence
    residual_confidence = values["avg_expected_margin_residual"] * confidence
    veto_credibility = clamp((pick_rate + max(0.0, 35.0 - ban_rate)) / 70.0, 0.0, 1.0)
    veto_strength = 50.0 + (adjusted_strength(values) - 50.0) * (0.35 + veto_credibility * 0.65)
    pick_ban_proxy = veto_credibility * (adjusted_strength(values) - 50.0) / 50.0
    bo1_upset_risk = max(0.0, 1.0 - confidence) * abs(win_edge) / 50.0
    bo3_depth = confidence * max(0.0, win_edge) / 50.0
    return {
        "vrs_tier_map_strength": adjusted_strength(values),
        "vrs_opponent_adjusted_scoreline_quality": values["opponent_adjusted_scoreline_quality"],
        "vrs_map_win_opponent_quality": opponent_quality_edge,
        "vrs_map_win_sample_confidence": win_sample_edge,
        "vrs_scoreline_sample_confidence": scoreline_sample,
        "vrs_map_veto_credibility": veto_credibility,
        "vrs_map_veto_strength": clamp(veto_strength, 5.0, 95.0),
        "vrs_pick_ban_opponent_pool_proxy": pick_ban_proxy,
        "vrs_bo1_single_map_upset_risk": bo1_upset_risk,
        "vrs_bo3_map_depth_strength": bo3_depth,
        "vrs_overtime_strong_opponent_signal": values["overtime_strong_opponent_signal"],
        "vrs_weak_opponent_close_penalty": values["weak_opponent_close_penalty"],
        "vrs_recent_strong_opponent_score": values["recent_strong_opponent_score"],
        "vrs_expected_margin_residual": values["avg_expected_margin_residual"],
        "vrs_expected_margin_residual_confidence": residual_confidence,
        "vrs_team_volatility": values["team_volatility"],
    }


def adjusted_strength(values: dict[str, float]) -> float:
    base = values["smoothed_win_rate"] + values["opponent_adjusted_scoreline_quality"] * 10.0
    base += values["avg_expected_margin_residual"] * 1.1
    base += values["recent_strong_opponent_score"] * 6.0
    base += values["overtime_strong_opponent_signal"] * 3.0
    base -= values["weak_opponent_close_penalty"] * 10.0
    confidence = 0.35 + values["sample_confidence"] * 0.65
    return clamp(50.0 + (base - 50.0) * confidence, 5.0, 95.0)


def win_rate(observations: list[Observation]) -> float:
    if not observations:
        return 0.5
    return sum(1 for item in observations if item.won) / len(observations)


def sample_confidence(maps: int) -> float:
    return min(1.0, maps / 10.0) if maps > 0 else 0.0


def opponent_strength_score(rank: int) -> float:
    return clamp((101.0 - rank) / 100.0, 0.0, 1.0)


def opponent_adjusted_scoreline(item: Observation) -> float:
    strength = opponent_strength_score(item.opponent_rank)
    quality = item.scoreline_quality
    if quality >= 0:
        adjusted = quality * (0.65 + 0.70 * strength)
        if item.won and item.opponent_rank > 50 and quality < 0.30:
            adjusted -= (0.30 - quality) * (1.0 - strength) * 0.80
        return adjusted
    return quality * (1.30 - 0.85 * strength)


def weak_opponent_close_penalty(item: Observation) -> float:
    if item.opponent_rank <= 50:
        return 0.0
    close_win = item.won and item.scoreline_quality < 0.30
    close_loss = (not item.won) and is_close_score(item.round_margin, 0)
    if not close_win and not close_loss:
        return 0.0
    return (1.0 - opponent_strength_score(item.opponent_rank)) * (0.5 if close_win else 1.0)


def recency_weight(item: Observation) -> float:
    if item.start_date is None:
        return 0.75
    reference = date(2026, 5, 25)
    age_days = max(0, (reference - item.start_date).days)
    return math.exp(-age_days / 60.0)


def standard_deviation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError:
            return None


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
    vrs_snapshots = sorted({item.vrs_snapshot_date for item in observations if item.vrs_snapshot_date})
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
            f"- VRS rank snapshots used: `{', '.join(vrs_snapshots)}`",
            "",
            "## Feature Design",
            "",
            "- Cumulative tiers: VRS top 10/20/30/40/50/70/100.",
            "- Diagnostic buckets: VRS 1-10, 11-20, 21-30, 31-40, 41-50, 51-70, 71-100.",
            "- Smoothed win rates use Bayesian shrinkage toward a blend of team-map baseline and global map baseline.",
            "- Scoreline quality is MR12/overtime aware: regulation margins scale strongly, overtime margins stay close to zero.",
            "- Interaction features combine scoreline quality with opponent VRS rank, map win rate with sample confidence, scoreline quality with sample confidence, map strength with pick/ban credibility, BO1 upset risk with BO3 map depth, close/overtime results with opponent strength, and recency with opponent quality.",
            "- Match-date VRS rank lookup uses the latest available Valve `standings_global_YYYY_MM_DD.md` snapshot at or before each BO3 match date; if none is older than the match, it falls back to the earliest available snapshot.",
            "- Expected-margin residual compares the actual map round margin against the margin implied by the two teams' VRS ranks, so narrow wins over weak opposition can become negative and close losses to strong opposition can become positive.",
            "- The map_veto-compatible win rate uses veto-credible map strength, so a strong map that is rarely picked or often banned is discounted before Swiss BO1/BO3 simulation.",
        ]
    ) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
