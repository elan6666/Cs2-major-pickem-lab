from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from .map_veto import (
    MapStatsByTeam,
    best_of_three_probability,
    map_win_probability,
    normalize_map_name,
    team_stat,
    veto_value,
)
from .models import Team


@dataclass(frozen=True)
class BanditPolicy:
    map_rewards: dict[str, float]
    action_rewards: dict[str, float]
    exploration: float = 0.20
    major_map_corrections: dict[str, float] = field(default_factory=dict)
    major_action_corrections: dict[str, float] = field(default_factory=dict)
    major_correction_weight: float = 0.0


def load_bandit_policy(path: str | Path) -> BanditPolicy:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return BanditPolicy(
        map_rewards={normalize_map_name(name): float(value) for name, value in payload.get("map_rewards", {}).items()},
        action_rewards={str(name): float(value) for name, value in payload.get("action_rewards", {}).items()},
        exploration=float(payload.get("exploration", 0.20)),
        major_map_corrections={normalize_map_name(name): float(value) for name, value in payload.get("major_map_corrections", {}).items()},
        major_action_corrections={str(name): float(value) for name, value in payload.get("major_action_corrections", {}).items()},
        major_correction_weight=float(payload.get("major_correction_weight", 0.0)),
    )


def train_bandit_policy_from_csv(path: str | Path, output_json: str | Path) -> dict[str, object]:
    stats = collect_reward_stats(path)
    payload = {
        "source": stats["source"],
        "example_count": stats["example_count"],
        "map_rewards": stats["map_rewards"],
        "action_rewards": stats["action_rewards"],
        "exploration": 0.20,
    }
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def train_two_layer_bandit_policy_from_csv(
    recent_path: str | Path,
    major_path: str | Path,
    output_json: str | Path,
    major_correction_weight: float = 0.50,
) -> dict[str, object]:
    if major_correction_weight < 0:
        raise ValueError("major correction weight must be non-negative")
    recent = collect_reward_stats(recent_path)
    major = collect_reward_stats(major_path)
    map_rewards = recent["map_rewards"]
    action_rewards = recent["action_rewards"]
    major_map_corrections = {
        name: float(value) - float(map_rewards.get(name, 0.5))
        for name, value in sorted(major["map_rewards"].items())
    }
    major_action_corrections = {
        name: float(value) - float(action_rewards.get(name, 0.5))
        for name, value in sorted(major["action_rewards"].items())
    }
    payload = {
        "mode": "two_layer_recent_bo3_with_major_correction",
        "recent_source": recent["source"],
        "major_source": major["source"],
        "recent_example_count": recent["example_count"],
        "major_example_count": major["example_count"],
        "map_rewards": map_rewards,
        "action_rewards": action_rewards,
        "major_map_corrections": major_map_corrections,
        "major_action_corrections": major_action_corrections,
        "major_correction_weight": major_correction_weight,
        "exploration": 0.20,
    }
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def collect_reward_stats(path: str | Path) -> dict[str, object]:
    map_totals: dict[str, list[float]] = {}
    action_totals: dict[str, list[float]] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            map_name = normalize_map_name(row.get("map", ""))
            action = row.get("action", "").strip().lower()
            reward = parse_reward(row)
            if map_name:
                map_totals.setdefault(map_name, []).append(reward)
            if action:
                action_totals.setdefault(action, []).append(reward)
    return {
        "source": str(path),
        "example_count": sum(len(values) for values in map_totals.values()),
        "map_rewards": {name: mean(values) for name, values in sorted(map_totals.items())},
        "action_rewards": {name: mean(values) for name, values in sorted(action_totals.items())},
    }


def bandit_veto_adjusted_win_probability(
    team_a: Team,
    team_b: Team,
    best_of: int,
    base_probability: float,
    map_pool: tuple[str, ...],
    map_stats: MapStatsByTeam,
    policy: BanditPolicy | None,
) -> float:
    available = tuple(normalize_map_name(name) for name in map_pool)
    if best_of == 3 and len(available) >= 7:
        selected = simulate_bo3_bandit_veto(team_a.name, team_b.name, available, map_stats, policy)
        map_probabilities = [map_win_probability(team_a.name, team_b.name, map_name, base_probability, map_stats) for map_name in selected]
        return best_of_three_probability(map_probabilities)
    selected_map = simulate_bo1_bandit_veto(team_a.name, team_b.name, available, map_stats, policy)
    return map_win_probability(team_a.name, team_b.name, selected_map, base_probability, map_stats)


def simulate_bo1_bandit_veto(
    team_a: str,
    team_b: str,
    map_pool: tuple[str, ...],
    map_stats: MapStatsByTeam,
    policy: BanditPolicy | None,
) -> str:
    remaining = list(map_pool)
    for actor in (team_a, team_a, team_b, team_b, team_b, team_a):
        if len(remaining) <= 1:
            break
        opponent = team_b if actor == team_a else team_a
        banned = choose_bandit_action(actor, opponent, remaining, map_stats, policy, "ban", maximize=False)
        remaining.remove(banned)
    return remaining[0]


def simulate_bo3_bandit_veto(
    team_a: str,
    team_b: str,
    map_pool: tuple[str, ...],
    map_stats: MapStatsByTeam,
    policy: BanditPolicy | None,
) -> tuple[str, str, str]:
    remaining = list(map_pool)
    remaining.remove(choose_bandit_action(team_a, team_b, remaining, map_stats, policy, "ban", maximize=False))
    remaining.remove(choose_bandit_action(team_b, team_a, remaining, map_stats, policy, "ban", maximize=False))
    first_pick = choose_bandit_action(team_a, team_b, remaining, map_stats, policy, "pick", maximize=True)
    remaining.remove(first_pick)
    second_pick = choose_bandit_action(team_b, team_a, remaining, map_stats, policy, "pick", maximize=True)
    remaining.remove(second_pick)
    remaining.remove(choose_bandit_action(team_b, team_a, remaining, map_stats, policy, "ban", maximize=False))
    remaining.remove(choose_bandit_action(team_a, team_b, remaining, map_stats, policy, "ban", maximize=False))
    return first_pick, second_pick, remaining[0]


def choose_bandit_action(
    team: str,
    opponent: str,
    remaining: list[str],
    map_stats: MapStatsByTeam,
    policy: BanditPolicy | None,
    action: str,
    maximize: bool,
) -> str:
    ranked = sorted(
        remaining,
        key=lambda map_name: (
            action_value(team, opponent, map_name, map_stats, policy, action),
            team_stat(team, map_name, map_stats).pick_rate,
            -team_stat(team, map_name, map_stats).ban_rate,
            map_name,
        ),
        reverse=maximize,
    )
    return ranked[0]


def action_value(
    team: str,
    opponent: str,
    map_name: str,
    map_stats: MapStatsByTeam,
    policy: BanditPolicy | None,
    action: str,
) -> float:
    base = veto_value(team, opponent, map_name, map_stats)
    if policy is None:
        return base
    prior = policy.map_rewards.get(normalize_map_name(map_name), 0.0)
    action_prior = policy.action_rewards.get(action, 0.0)
    major_prior = policy.major_map_corrections.get(normalize_map_name(map_name), 0.0) * policy.major_correction_weight
    major_action_prior = policy.major_action_corrections.get(action, 0.0) * policy.major_correction_weight
    exploration_bonus = policy.exploration / math.sqrt(1.0 + max(team_stat(team, map_name, map_stats).maps_played, 0))
    return base + (prior + major_prior) * 0.20 + (action_prior + major_action_prior) * 0.08 + exploration_bonus


def parse_reward(row: Mapping[str, str]) -> float:
    for field in ("reward", "map_won", "match_won", "winner"):
        value = row.get(field)
        if value is None or value.strip() == "":
            continue
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "win", "won"}:
            return 1.0
        if lowered in {"false", "no", "loss", "lost"}:
            return 0.0
        return float(value)
    return 0.5


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
