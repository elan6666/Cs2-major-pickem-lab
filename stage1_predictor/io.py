from __future__ import annotations

import csv
from pathlib import Path

from .models import MatchResult, Team


def load_teams(path: str | Path) -> list[Team]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    teams: list[Team] = []
    for row in rows:
        try:
            team = Team(
                seed=int(row["seed"]),
                name=row["team"].strip(),
                score=float(row["score"]),
                region=row.get("region", "").strip(),
                notes=row.get("notes", "").strip(),
            )
        except KeyError as exc:
            raise ValueError(f"Missing required teams CSV column: {exc.args[0]}") from exc
        if not team.name:
            raise ValueError("Team name cannot be empty")
        teams.append(team)

    validate_teams(teams)
    return sorted(teams, key=lambda team: team.seed)


def validate_teams(teams: list[Team]) -> None:
    if len(teams) != 16:
        raise ValueError(f"Stage 1 requires exactly 16 teams, got {len(teams)}")

    names = [team.name for team in teams]
    if len(set(names)) != len(names):
        raise ValueError("Team names must be unique")

    seeds = [team.seed for team in teams]
    if sorted(seeds) != list(range(1, 17)):
        raise ValueError("Seeds must be exactly 1 through 16")


def load_locked_results(path: str | Path | None) -> list[MatchResult]:
    if path is None:
        return []

    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    results: list[MatchResult] = []
    for row in rows:
        try:
            best_of = int(row.get("best_of") or 0)
            results.append(
                MatchResult(
                    round_number=int(row["round"]),
                    winner=row["winner"].strip(),
                    loser=row["loser"].strip(),
                    best_of=best_of,
                )
            )
        except KeyError as exc:
            raise ValueError(f"Missing required locked results CSV column: {exc.args[0]}") from exc
    return results
