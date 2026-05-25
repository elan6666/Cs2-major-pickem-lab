from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Mapping

from .bandit_veto import BanditPolicy, bandit_veto_adjusted_win_probability
from .map_veto import MapStat, veto_adjusted_win_probability
from .models import MatchResult, SimulationOutcome, Team, TeamState

SIX_TEAM_PAIRING_PRIORITY = (
    ((1, 6), (2, 5), (3, 4)),
    ((1, 6), (2, 4), (3, 5)),
    ((1, 5), (2, 6), (3, 4)),
    ((1, 5), (2, 4), (3, 6)),
    ((1, 4), (2, 6), (3, 5)),
    ((1, 4), (2, 5), (3, 6)),
    ((1, 6), (2, 3), (4, 5)),
    ((1, 5), (2, 3), (4, 6)),
    ((1, 3), (2, 6), (4, 5)),
    ((1, 3), (2, 5), (4, 6)),
    ((1, 4), (2, 3), (5, 6)),
    ((1, 3), (2, 4), (5, 6)),
    ((1, 2), (3, 6), (4, 5)),
    ((1, 2), (3, 5), (4, 6)),
    ((1, 2), (3, 4), (5, 6)),
)


@dataclass(frozen=True)
class SimulationConfig:
    scale: float = 120.0
    bo1_shrink: float = 0.70
    bo3_shrink: float = 1.00
    veto_weight: float = 1.00
    all_bo3: bool = False
    min_probability: float = 0.05
    max_probability: float = 0.95
    map_pool: tuple[str, ...] = ()
    map_stats: Mapping[str, Mapping[str, MapStat]] | None = None
    veto_policy: str = "greedy"
    bandit_policy: BanditPolicy | None = None


def base_win_probability(team_a: Team, team_b: Team, scale: float) -> float:
    if scale <= 0:
        raise ValueError("scale must be greater than 0")
    diff = team_a.score - team_b.score
    return 1.0 / (1.0 + math.exp(-diff / scale))


def adjusted_win_probability(
    team_a: Team,
    team_b: Team,
    best_of: int,
    config: SimulationConfig,
) -> float:
    raw = base_win_probability(team_a, team_b, config.scale)
    if config.map_pool and config.map_stats:
        if config.veto_policy == "contextual-bandit":
            veto_raw = bandit_veto_adjusted_win_probability(
                team_a,
                team_b,
                best_of,
                raw,
                config.map_pool,
                config.map_stats,
                config.bandit_policy,
            )
        else:
            veto_raw = veto_adjusted_win_probability(team_a, team_b, best_of, raw, config.map_pool, config.map_stats)
        raw += (veto_raw - raw) * config.veto_weight
    shrink = config.bo3_shrink if best_of == 3 else config.bo1_shrink
    adjusted = 0.5 + (raw - 0.5) * shrink
    return min(config.max_probability, max(config.min_probability, adjusted))


def simulate_stage(
    teams: list[Team],
    rng: random.Random,
    config: SimulationConfig,
    locked_results: list[MatchResult] | None = None,
) -> SimulationOutcome:
    states = {team.name: TeamState(team=team) for team in teams}
    locked_results = locked_results or []
    for result in locked_results:
        apply_result(states, result)

    round_number = (max((result.round_number for result in locked_results), default=0) + 1)
    while any(state.active for state in states.values()):
        pairings = pair_round(list(states.values()))
        for left, right in pairings:
            best_of = choose_best_of(left, right, config)
            left_probability = adjusted_win_probability(left.team, right.team, best_of, config)
            if rng.random() < left_probability:
                winner, loser = left.team.name, right.team.name
            else:
                winner, loser = right.team.name, left.team.name
            apply_result(
                states,
                MatchResult(
                    round_number=round_number,
                    winner=winner,
                    loser=loser,
                    best_of=best_of,
                ),
            )
        round_number += 1

    records = {name: state.record for name, state in states.items()}
    advanced = frozenset(name for name, record in records.items() if record[0] == 3)
    three_zero = frozenset(name for name, record in records.items() if record == (3, 0))
    zero_three = frozenset(name for name, record in records.items() if record == (0, 3))
    if len(advanced) != 8:
        raise RuntimeError(f"Swiss simulation ended with {len(advanced)} advanced teams")
    return SimulationOutcome(records=records, advanced=advanced, three_zero=three_zero, zero_three=zero_three)


def apply_result(states: dict[str, TeamState], result: MatchResult) -> None:
    if result.winner not in states:
        raise ValueError(f"Unknown locked result winner: {result.winner}")
    if result.loser not in states:
        raise ValueError(f"Unknown locked result loser: {result.loser}")
    if result.winner == result.loser:
        raise ValueError("Winner and loser cannot be the same team")

    winner = states[result.winner]
    loser = states[result.loser]
    if not winner.active or not loser.active:
        raise ValueError("Locked result includes a team that is already advanced or eliminated")

    winner.wins += 1
    loser.losses += 1
    winner.opponents.add(loser.team.name)
    loser.opponents.add(winner.team.name)


def choose_best_of(left: TeamState, right: TeamState, config: SimulationConfig) -> int:
    if config.all_bo3:
        return 3
    if left.wins == 2 or right.wins == 2 or left.losses == 2 or right.losses == 2:
        return 3
    return 1


def pair_round(states: list[TeamState]) -> list[tuple[TeamState, TeamState]]:
    active = [state for state in states if state.active]
    if not any(state.opponents for state in active):
        ordered = sorted(active, key=lambda state: state.team.seed)
        return list(zip(ordered[:8], ordered[8:], strict=True))

    stage_index = max((state.wins + state.losses for state in active), default=0)
    groups: dict[tuple[int, int], list[TeamState]] = defaultdict(list)
    for state in active:
        groups[state.record].append(state)

    pairings: list[tuple[TeamState, TeamState]] = []
    for record in sorted(groups, key=lambda item: (-item[0], item[1])):
        group = sort_group(groups[record], states)
        pairings.extend(pair_group_without_rematches(group, stage_index=stage_index))
    return pairings


def sort_group(group: list[TeamState], all_states: list[TeamState]) -> list[TeamState]:
    return sorted(
        group,
        key=lambda state: (
            -state.wins,
            state.losses,
            -difficulty_score(state, all_states),
            state.team.seed,
        ),
    )


def difficulty_score(state: TeamState, all_states: list[TeamState]) -> int:
    by_name = {candidate.team.name: candidate for candidate in all_states}
    return sum(by_name[opponent].wins - by_name[opponent].losses for opponent in state.opponents)


def pair_group_without_rematches(
    group: list[TeamState],
    stage_index: int = 0,
) -> list[tuple[TeamState, TeamState]]:
    if len(group) % 2 != 0:
        raise ValueError("Swiss record group has an odd number of active teams")
    if len(group) == 6:
        priority_pairings = pair_six_team_group_by_valve_priority(group)
        if priority_pairings is not None:
            return priority_pairings
    paired = _pair_group_recursive(tuple(group), stage_index=stage_index, pool_size=len(group))
    if paired is not None:
        return paired

    # Fallback for inconsistent locked results: keep the stage runnable and make the limitation visible.
    return [(group[i], group[-i - 1]) for i in range(len(group) // 2)]


def pair_six_team_group_by_valve_priority(group: list[TeamState]) -> list[tuple[TeamState, TeamState]] | None:
    """Apply Valve's six-team Swiss pairing priority table for rounds 4 and 5."""
    by_position = {index + 1: state for index, state in enumerate(group)}
    for pattern in SIX_TEAM_PAIRING_PRIORITY:
        pairings = [(by_position[left], by_position[right]) for left, right in pattern]
        if all(right.team.name not in left.opponents for left, right in pairings):
            return pairings
    return None


def _pair_group_recursive(
    group: tuple[TeamState, ...],
    stage_index: int = 0,
    pool_size: int | None = None,
) -> list[tuple[TeamState, TeamState]] | None:
    indexed_group = tuple(enumerate(group))
    result = _pair_group_recursive_scored(indexed_group, stage_index=stage_index, pool_size=pool_size or len(group))
    return None if result is None else result[1]


def _pair_group_recursive_scored(
    group: tuple[tuple[int, TeamState], ...],
    stage_index: int,
    pool_size: int,
) -> tuple[int, list[tuple[TeamState, TeamState]]] | None:
    if not group:
        return 0, []

    first_index, first = group[0]
    candidates = list(range(len(group) - 1, 0, -1))
    best: tuple[int, list[tuple[TeamState, TeamState]]] | None = None
    for index in candidates:
        second_index, second = group[index]
        if second.team.name in first.opponents:
            continue
        remainder = group[1:index] + group[index + 1 :]
        rest = _pair_group_recursive_scored(
            remainder,
            stage_index=stage_index,
            pool_size=pool_size,
        )
        if rest is None:
            continue
        score = second_index - first_index + rest[0]
        matches = [(first, second)] + rest[1]
        if stage_index <= 2:
            return score, matches
        if best is None or score > best[0]:
            best = score, matches
    return best


def run_simulations(
    teams: list[Team],
    simulations: int,
    seed: int,
    config: SimulationConfig,
    locked_results: list[MatchResult] | None = None,
) -> list[SimulationOutcome]:
    if simulations <= 0:
        raise ValueError("simulations must be greater than 0")
    rng = random.Random(seed)
    return [simulate_stage(teams, rng, config, locked_results) for _ in range(simulations)]


def enumerate_possible_first_round(teams: list[Team]) -> list[tuple[str, str]]:
    ordered = sorted(teams, key=lambda team: team.seed)
    return [(left.name, right.name) for left, right in zip(ordered[:8], ordered[8:], strict=True)]


def possible_records() -> list[str]:
    return ["3-0", "3-1", "3-2", "2-3", "1-3", "0-3"]


def record_key(record: tuple[int, int]) -> str:
    return f"{record[0]}-{record[1]}"


def all_pair_names(pairings: list[tuple[TeamState, TeamState]]) -> set[frozenset[str]]:
    return {frozenset((left.team.name, right.team.name)) for left, right in pairings}


def has_duplicate_pairings(results: list[MatchResult]) -> bool:
    seen: set[frozenset[str]] = set()
    for result in results:
        pair = frozenset((result.winner, result.loser))
        if pair in seen:
            return True
        seen.add(pair)
    return False


def possible_card_count(team_count: int, three_zero_picks: int, zero_three_picks: int, advance_picks: int) -> int:
    remaining_after_specials = team_count - three_zero_picks - zero_three_picks
    if remaining_after_specials < advance_picks:
        return 0
    return math.comb(team_count, three_zero_picks) * math.comb(team_count - three_zero_picks, zero_three_picks) * math.comb(remaining_after_specials, advance_picks)


def unique_name_combinations(names: list[str], count: int) -> list[tuple[str, ...]]:
    return list(combinations(names, count))
