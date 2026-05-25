from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Team:
    seed: int
    name: str
    score: float
    region: str = ""
    notes: str = ""


@dataclass
class TeamState:
    team: Team
    wins: int = 0
    losses: int = 0
    opponents: set[str] = field(default_factory=set)

    @property
    def active(self) -> bool:
        return self.wins < 3 and self.losses < 3

    @property
    def record(self) -> tuple[int, int]:
        return (self.wins, self.losses)


@dataclass(frozen=True)
class MatchResult:
    round_number: int
    winner: str
    loser: str
    best_of: int


@dataclass(frozen=True)
class SimulationOutcome:
    records: dict[str, tuple[int, int]]
    advanced: frozenset[str]
    three_zero: frozenset[str]
    zero_three: frozenset[str]


@dataclass(frozen=True)
class TeamProbability:
    team: Team
    record_probabilities: dict[str, float]

    @property
    def advance_probability(self) -> float:
        return (
            self.record_probabilities.get("3-0", 0.0)
            + self.record_probabilities.get("3-1", 0.0)
            + self.record_probabilities.get("3-2", 0.0)
        )

    @property
    def most_common_record(self) -> str:
        return max(self.record_probabilities.items(), key=lambda item: item[1])[0]


@dataclass(frozen=True)
class PickemCard:
    three_zero: tuple[str, ...]
    zero_three: tuple[str, ...]
    advance: tuple[str, ...]
    pass_probability: float
    expected_correct: float
