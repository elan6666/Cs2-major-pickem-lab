from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .models import Team


DEFAULT_MAP_POOL = ("Ancient", "Anubis", "Dust2", "Inferno", "Mirage", "Nuke", "Overpass")


@dataclass(frozen=True)
class MapStat:
    team: str
    map_name: str
    win_rate: float
    maps_played: int = 0
    pick_rate: float = 0.0
    ban_rate: float = 0.0
    pistol_win_rate: float | None = None
    first_kill_round_win_rate: float | None = None
    first_death_round_win_rate: float | None = None
    source: str = ""

    @property
    def confidence(self) -> float:
        return min(1.0, self.maps_played / 8.0) if self.maps_played > 0 else 0.0


MapStatsByTeam = Mapping[str, Mapping[str, MapStat]]


def parse_map_pool(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_MAP_POOL
    maps = tuple(item.strip() for item in value.split(",") if item.strip())
    if len(maps) < 3:
        raise ValueError("--map-pool must contain at least 3 maps")
    return maps


def load_map_stats(path: str | Path) -> dict[str, dict[str, MapStat]]:
    output: dict[str, dict[str, MapStat]] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            team = row.get("team", "").strip()
            map_name = normalize_map_name(row.get("map", ""))
            if not team or not map_name:
                continue
            output.setdefault(team, {})[map_name] = MapStat(
                team=team,
                map_name=map_name,
                win_rate=parse_percent(row.get("win_rate"), default=50.0),
                maps_played=int(parse_number(row.get("maps_played"), default=0.0)),
                pick_rate=parse_percent(row.get("pick_rate"), default=0.0),
                ban_rate=parse_percent(row.get("ban_rate"), default=0.0),
                pistol_win_rate=parse_optional_percent(row.get("pistol_win_rate")),
                first_kill_round_win_rate=parse_optional_percent(row.get("first_kill_round_win_rate")),
                first_death_round_win_rate=parse_optional_percent(row.get("first_death_round_win_rate")),
                source=row.get("source", "").strip(),
            )
    return output


def veto_adjusted_win_probability(
    team_a: Team,
    team_b: Team,
    best_of: int,
    base_probability: float,
    map_pool: tuple[str, ...],
    map_stats: MapStatsByTeam,
) -> float:
    available_maps = tuple(normalize_map_name(name) for name in map_pool)
    if len(available_maps) < 3:
        return base_probability
    if best_of == 3 and len(available_maps) >= 7:
        selected = simulate_bo3_veto(team_a.name, team_b.name, available_maps, map_stats)
        map_probabilities = [map_win_probability(team_a.name, team_b.name, map_name, base_probability, map_stats) for map_name in selected]
        return best_of_three_probability(map_probabilities)

    selected_map = simulate_bo1_veto(team_a.name, team_b.name, available_maps, map_stats)
    return map_win_probability(team_a.name, team_b.name, selected_map, base_probability, map_stats)


def simulate_bo1_veto(team_a: str, team_b: str, map_pool: tuple[str, ...], map_stats: MapStatsByTeam) -> str:
    remaining = list(map_pool)
    for actor in (team_a, team_a, team_b, team_b, team_b, team_a):
        if len(remaining) <= 1:
            break
        opponent = team_b if actor == team_a else team_a
        banned = choose_ban(actor, opponent, remaining, map_stats)
        remaining.remove(banned)
    return remaining[0]


def simulate_bo3_veto(team_a: str, team_b: str, map_pool: tuple[str, ...], map_stats: MapStatsByTeam) -> tuple[str, str, str]:
    remaining = list(map_pool)
    remaining.remove(choose_ban(team_a, team_b, remaining, map_stats))
    remaining.remove(choose_ban(team_b, team_a, remaining, map_stats))
    first_pick = choose_pick(team_a, team_b, remaining, map_stats)
    remaining.remove(first_pick)
    second_pick = choose_pick(team_b, team_a, remaining, map_stats)
    remaining.remove(second_pick)
    remaining.remove(choose_ban(team_b, team_a, remaining, map_stats))
    remaining.remove(choose_ban(team_a, team_b, remaining, map_stats))
    return first_pick, second_pick, remaining[0]


def choose_ban(team: str, opponent: str, remaining: list[str], map_stats: MapStatsByTeam) -> str:
    return min(
        remaining,
        key=lambda map_name: (
            veto_value(team, opponent, map_name, map_stats),
            -team_stat(team, map_name, map_stats).ban_rate,
            team_stat(team, map_name, map_stats).pick_rate,
            map_name,
        ),
    )


def choose_pick(team: str, opponent: str, remaining: list[str], map_stats: MapStatsByTeam) -> str:
    return max(
        remaining,
        key=lambda map_name: (
            veto_value(team, opponent, map_name, map_stats),
            team_stat(team, map_name, map_stats).pick_rate,
            -team_stat(team, map_name, map_stats).ban_rate,
            map_name,
        ),
    )


def veto_value(team: str, opponent: str, map_name: str, map_stats: MapStatsByTeam) -> float:
    own = team_stat(team, map_name, map_stats)
    other = team_stat(opponent, map_name, map_stats)
    win_edge = own_adjusted_win_rate(own) - own_adjusted_win_rate(other)
    comfort = own.pick_rate * 0.15 - own.ban_rate * 0.12
    opponent_comfort = other.pick_rate * 0.08 - other.ban_rate * 0.05
    return win_edge + comfort - opponent_comfort


def map_win_probability(
    team_a: str,
    team_b: str,
    map_name: str,
    base_probability: float,
    map_stats: MapStatsByTeam,
) -> float:
    stat_a = team_stat(team_a, map_name, map_stats)
    stat_b = team_stat(team_b, map_name, map_stats)
    if stat_a.confidence == 0 and stat_b.confidence == 0:
        return base_probability
    edge = (own_adjusted_win_rate(stat_a) - own_adjusted_win_rate(stat_b)) / 100.0
    comfort_edge = (stat_a.pick_rate - stat_b.pick_rate - stat_a.ban_rate + stat_b.ban_rate) / 100.0
    economy_edge = optional_edge(stat_a.pistol_win_rate, stat_b.pistol_win_rate) * 0.08
    first_kill_edge = optional_edge(stat_a.first_kill_round_win_rate, stat_b.first_kill_round_win_rate) * 0.06
    first_death_edge = optional_edge(stat_a.first_death_round_win_rate, stat_b.first_death_round_win_rate) * 0.04
    logit = probability_logit(base_probability)
    logit += edge * 1.15 + comfort_edge * 0.35 + economy_edge + first_kill_edge + first_death_edge
    return min(0.95, max(0.05, 1.0 / (1.0 + math.exp(-logit))))


def own_adjusted_win_rate(stat: MapStat) -> float:
    confidence = stat.confidence
    return 50.0 + (stat.win_rate - 50.0) * confidence


def team_stat(team: str, map_name: str, map_stats: MapStatsByTeam) -> MapStat:
    return map_stats.get(team, {}).get(normalize_map_name(map_name), MapStat(team=team, map_name=normalize_map_name(map_name), win_rate=50.0))


def best_of_three_probability(map_probabilities: list[float]) -> float:
    if len(map_probabilities) != 3:
        raise ValueError("BO3 probability requires exactly three map probabilities")
    p1, p2, p3 = map_probabilities
    return p1 * p2 + p1 * (1 - p2) * p3 + (1 - p1) * p2 * p3


def probability_logit(value: float) -> float:
    value = min(0.999, max(0.001, value))
    return math.log(value / (1.0 - value))


def optional_edge(left: float | None, right: float | None) -> float:
    if left is None or right is None:
        return 0.0
    return (left - right) / 100.0


def parse_percent(value: str | None, default: float) -> float:
    return parse_number(value, default)


def parse_optional_percent(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return parse_number(value, 0.0)


def parse_number(value: str | None, default: float) -> float:
    if value is None or value.strip() == "":
        return default
    return float(value.strip().replace("%", ""))


def normalize_map_name(value: str) -> str:
    normalized = value.strip().replace(" ", "")
    aliases = {
        "DustII": "Dust2",
        "de_ancient": "Ancient",
        "de_anubis": "Anubis",
        "de_dust2": "Dust2",
        "de_inferno": "Inferno",
        "de_mirage": "Mirage",
        "de_nuke": "Nuke",
        "de_overpass": "Overpass",
        "de_train": "Train",
    }
    return aliases.get(normalized, normalized)
