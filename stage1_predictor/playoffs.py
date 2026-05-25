from __future__ import annotations

import csv
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .models import Team
from .swiss import SimulationConfig, adjusted_win_probability


@dataclass(frozen=True)
class PlayoffMatch:
    round_name: str
    left_seed: int
    right_seed: int
    best_of: int = 3


@dataclass(frozen=True)
class PlayoffOutcome:
    semifinalists: frozenset[str]
    finalists: frozenset[str]
    champion: str


DEFAULT_QUARTERFINAL_PAIRINGS = (
    PlayoffMatch("quarterfinal", 1, 8, 3),
    PlayoffMatch("quarterfinal", 4, 5, 3),
    PlayoffMatch("quarterfinal", 2, 7, 3),
    PlayoffMatch("quarterfinal", 3, 6, 3),
)


def load_playoff_teams(path: str | Path) -> list[Team]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    teams: list[Team] = []
    for row in rows:
        teams.append(
            Team(
                seed=int(row["seed"]),
                name=row["team"].strip(),
                score=float(row["score"]),
                region=row.get("region", "").strip(),
                notes=row.get("notes", "").strip(),
            )
        )
    validate_playoff_teams(teams)
    return sorted(teams, key=lambda team: team.seed)


def validate_playoff_teams(teams: list[Team]) -> None:
    if len(teams) != 8:
        raise ValueError(f"Playoffs require exactly 8 teams, got {len(teams)}")
    names = [team.name for team in teams]
    if len(set(names)) != len(names):
        raise ValueError("Playoff team names must be unique")
    seeds = [team.seed for team in teams]
    if sorted(seeds) != list(range(1, 9)):
        raise ValueError("Playoff seeds must be exactly 1 through 8")


def simulate_playoffs(
    teams: list[Team],
    rng: random.Random,
    config: SimulationConfig,
    final_best_of: int = 3,
) -> PlayoffOutcome:
    by_seed = {team.seed: team for team in teams}
    semifinalists: list[Team] = []
    for match in DEFAULT_QUARTERFINAL_PAIRINGS:
        semifinalists.append(simulate_match(by_seed[match.left_seed], by_seed[match.right_seed], match.best_of, rng, config))

    finalist_left = simulate_match(semifinalists[0], semifinalists[1], 3, rng, config)
    finalist_right = simulate_match(semifinalists[2], semifinalists[3], 3, rng, config)
    champion = simulate_match(finalist_left, finalist_right, final_best_of, rng, config)
    return PlayoffOutcome(
        semifinalists=frozenset(team.name for team in semifinalists),
        finalists=frozenset((finalist_left.name, finalist_right.name)),
        champion=champion.name,
    )


def simulate_match(
    left: Team,
    right: Team,
    best_of: int,
    rng: random.Random,
    config: SimulationConfig,
) -> Team:
    left_probability = adjusted_win_probability(left, right, best_of, config)
    return left if rng.random() < left_probability else right


def run_playoff_simulations(
    teams: list[Team],
    simulations: int,
    seed: int,
    config: SimulationConfig,
    final_best_of: int = 3,
) -> list[PlayoffOutcome]:
    if simulations <= 0:
        raise ValueError("simulations must be greater than 0")
    if final_best_of not in {3, 5}:
        raise ValueError("final_best_of must be 3 or 5")
    validate_playoff_teams(teams)
    rng = random.Random(seed)
    return [simulate_playoffs(teams, rng, config, final_best_of) for _ in range(simulations)]


def summarize_playoff_probabilities(
    teams: list[Team],
    outcomes: list[PlayoffOutcome],
) -> list[dict[str, object]]:
    total = len(outcomes)
    semifinal_counts: Counter[str] = Counter()
    final_counts: Counter[str] = Counter()
    champion_counts: Counter[str] = Counter()
    for outcome in outcomes:
        semifinal_counts.update(outcome.semifinalists)
        final_counts.update(outcome.finalists)
        champion_counts.update([outcome.champion])

    rows: list[dict[str, object]] = []
    for team in teams:
        rows.append(
            {
                "team": team.name,
                "seed": team.seed,
                "score": team.score,
                "p_semifinal": semifinal_counts[team.name] / total,
                "p_final": final_counts[team.name] / total,
                "p_champion": champion_counts[team.name] / total,
            }
        )
    return sorted(rows, key=lambda row: (-float(row["p_champion"]), int(row["seed"])))


def render_playoff_report(
    rows: list[dict[str, object]],
    settings: dict[str, object],
) -> str:
    lines = [
        "# CS2 Major Playoffs 预测报告",
        "",
        "## 运行设置",
        "",
    ]
    for key, value in settings.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## 淘汰赛概率",
            "",
            "| 队伍 | 种子 | 分数 | 半决赛 | 决赛 | 冠军 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {team} | {seed} | {score:.1f} | {p_semifinal:.1%} | {p_final:.1%} | {p_champion:.1%} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## 注意事项",
            "",
            "- 真实 Major 预测前需要官方 Playoffs 队伍和种子。",
            "- bracket 默认顺序为 1v8、4v5、2v7、3v6。",
            "- 单场胜率使用与 Swiss 模拟器相同的队伍分数模型。",
        ]
    )
    return "\n".join(lines) + "\n"


def write_playoff_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["team", "seed", "score", "p_semifinal", "p_final", "p_champion"])
        writer.writeheader()
        writer.writerows(rows)


def write_playoff_json(path: str | Path, rows: list[dict[str, object]], settings: dict[str, object]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    payload = {"settings": settings, "probabilities": rows}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
