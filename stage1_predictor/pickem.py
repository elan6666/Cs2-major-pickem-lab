from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from .models import PickemCard, SimulationOutcome, Team, TeamProbability
from .swiss import possible_records, record_key


@dataclass(frozen=True)
class PickemConfig:
    pass_threshold: int = 5
    three_zero_picks: int = 2
    zero_three_picks: int = 2
    advance_picks: int = 6
    three_zero_pool: int = 5
    zero_three_pool: int = 5
    advance_pool: int = 10


def summarize_probabilities(teams: list[Team], outcomes: list[SimulationOutcome]) -> list[TeamProbability]:
    counts: dict[str, Counter[str]] = {team.name: Counter() for team in teams}
    for outcome in outcomes:
        for team_name, record in outcome.records.items():
            counts[team_name][record_key(record)] += 1

    total = len(outcomes)
    by_name = {team.name: team for team in teams}
    probabilities: list[TeamProbability] = []
    for name, counter in counts.items():
        record_probabilities = {record: counter[record] / total for record in possible_records()}
        probabilities.append(TeamProbability(team=by_name[name], record_probabilities=record_probabilities))

    return sorted(probabilities, key=lambda item: (-item.advance_probability, item.team.seed))


def recommend_pickem_card(
    probabilities: list[TeamProbability],
    outcomes: list[SimulationOutcome],
    config: PickemConfig,
) -> PickemCard:
    names = [probability.team.name for probability in probabilities]
    if config.pass_threshold <= 0:
        raise ValueError("pass_threshold must be greater than 0")
    if config.three_zero_picks < 0 or config.zero_three_picks < 0 or config.advance_picks < 0:
        raise ValueError("pick counts cannot be negative")
    if config.three_zero_picks + config.zero_three_picks + config.advance_picks > len(names):
        raise ValueError("pick counts exceed team count")

    by_name = {probability.team.name: probability for probability in probabilities}
    three_zero_pool = sorted(
        names,
        key=lambda name: (
            -by_name[name].record_probabilities["3-0"],
            -by_name[name].advance_probability,
        ),
    )[: config.three_zero_pool]
    zero_three_pool = sorted(
        names,
        key=lambda name: (
            -by_name[name].record_probabilities["0-3"],
            by_name[name].advance_probability,
        ),
    )[: config.zero_three_pool]
    advance_pool = sorted(names, key=lambda name: -by_name[name].pickem_advance_probability)[: config.advance_pool]

    best: PickemCard | None = None
    for three_zero in combinations(three_zero_pool, config.three_zero_picks):
        three_zero_set = set(three_zero)
        for zero_three in combinations(zero_three_pool, config.zero_three_picks):
            zero_three_set = set(zero_three)
            if three_zero_set & zero_three_set:
                continue
            special_picks = three_zero_set | zero_three_set
            eligible_advance = [name for name in advance_pool if name not in special_picks]
            if len(eligible_advance) < config.advance_picks:
                eligible_advance = [name for name in names if name not in special_picks]
                eligible_advance = sorted(
                    eligible_advance,
                    key=lambda name: -by_name[name].pickem_advance_probability,
                )[: max(config.advance_picks, config.advance_pool)]

            for advance in combinations(eligible_advance, config.advance_picks):
                candidate = evaluate_card(
                    outcomes,
                    three_zero=three_zero,
                    zero_three=zero_three,
                    advance=advance,
                    pass_threshold=config.pass_threshold,
                )
                if best is None or (
                    candidate.pass_probability,
                    candidate.expected_correct,
                ) > (
                    best.pass_probability,
                    best.expected_correct,
                ):
                    best = candidate

    if best is None:
        raise RuntimeError("Unable to build a Pick'Em recommendation")
    return best


def evaluate_card(
    outcomes: list[SimulationOutcome],
    three_zero: tuple[str, ...],
    zero_three: tuple[str, ...],
    advance: tuple[str, ...],
    pass_threshold: int,
) -> PickemCard:
    passed = 0
    total_correct = 0
    three_zero_set = set(three_zero)
    zero_three_set = set(zero_three)
    advance_set = set(advance)

    for outcome in outcomes:
        correct = 0
        correct += len(three_zero_set & set(outcome.three_zero))
        correct += len(zero_three_set & set(outcome.zero_three))
        pickem_advanced = {team for team, record in outcome.records.items() if record in {(3, 1), (3, 2)}}
        correct += len(advance_set & pickem_advanced)
        total_correct += correct
        if correct >= pass_threshold:
            passed += 1

    total = len(outcomes)
    return PickemCard(
        three_zero=three_zero,
        zero_three=zero_three,
        advance=advance,
        pass_probability=passed / total,
        expected_correct=total_correct / total,
    )
