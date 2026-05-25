from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from .models import Team
from .snapshots import validate_snapshot
from .train_stage1_model import TARGETS, LogisticModel, build_features, population_std


@dataclass(frozen=True)
class TeamModelScore:
    team: Team
    probability: float
    original_score: float


def load_final_model(model_json_path: str | Path, target: str) -> LogisticModel:
    if target not in TARGETS:
        raise ValueError(f"Unsupported model target '{target}'. Expected one of: {', '.join(TARGETS)}")
    payload = json.loads(Path(model_json_path).read_text(encoding="utf-8"))
    try:
        weights = payload["final_models"][target]["weights"]
    except KeyError as exc:
        raise ValueError(f"Model JSON does not include final model target '{target}'") from exc
    return LogisticModel(tuple(float(weight) for weight in weights))


def build_model_scored_teams(
    teams: list[Team],
    snapshot_path: str | Path,
    model_json_path: str | Path,
    target: str,
    score_scale: float,
) -> list[Team]:
    model_scores = score_teams_with_model(teams, snapshot_path, model_json_path, target, score_scale)
    return [item.team for item in model_scores]


def score_teams_with_model(
    teams: list[Team],
    snapshot_path: str | Path,
    model_json_path: str | Path,
    target: str,
    score_scale: float,
) -> list[TeamModelScore]:
    result = validate_snapshot(snapshot_path)
    if not result.ok:
        raise ValueError(f"Invalid snapshot {snapshot_path}: {'; '.join(result.errors)}")

    rows = load_snapshot_rows(snapshot_path)
    validate_snapshot_matches_teams(teams, rows)
    model = load_final_model(model_json_path, target)

    scores = [float(row["score"]) for row in rows]
    seeds = [float(row["seed"]) for row in rows]
    score_mean = sum(scores) / len(scores)
    seed_mean = sum(seeds) / len(seeds)
    score_std = population_std(scores) or 1.0
    seed_std = population_std(seeds) or 1.0
    row_by_team = {row["team"]: row for row in rows}

    model_scores: list[TeamModelScore] = []
    for team in teams:
        row = row_by_team[team.name]
        features = build_features(row, score_mean, score_std, seed_mean, seed_std)
        probability = clamp_probability(model.predict(features))
        model_score = logit(probability) * score_scale
        notes = append_note(
            team.notes,
            f"model_target={target}; model_probability={probability:.6f}; original_score={team.score:.1f}",
        )
        model_scores.append(
            TeamModelScore(
                team=Team(
                    seed=team.seed,
                    name=team.name,
                    score=model_score,
                    region=team.region,
                    notes=notes,
                ),
                probability=probability,
                original_score=team.score,
            )
        )
    return model_scores


def load_snapshot_rows(snapshot_path: str | Path) -> list[dict[str, str]]:
    with Path(snapshot_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_snapshot_matches_teams(teams: list[Team], rows: list[dict[str, str]]) -> None:
    team_names = {team.name for team in teams}
    snapshot_names = {row.get("team", "") for row in rows}
    missing = sorted(team_names - snapshot_names)
    extra = sorted(snapshot_names - team_names)
    if missing:
        raise ValueError(f"Snapshot is missing teams from teams CSV: {', '.join(missing)}")
    if extra:
        raise ValueError(f"Snapshot has teams not present in teams CSV: {', '.join(extra)}")


def append_note(existing: str, note: str) -> str:
    if not existing:
        return note
    return f"{existing}; {note}"


def clamp_probability(value: float) -> float:
    return min(max(value, 1e-6), 1 - 1e-6)


def logit(value: float) -> float:
    value = clamp_probability(value)
    return math.log(value / (1 - value))
