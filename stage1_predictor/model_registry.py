from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .catboost_model import score_teams_with_catboost
from .models import Team
from .snapshots import BLOCKED_FEATURE_COLUMNS
from .trained_model import build_model_scored_teams, validate_snapshot_matches_teams


MODEL_CHOICES = ("vrs", "feature-score", "factor-score", "logistic", "elo", "glicko", "catboost", "xgboost", "lightgbm")
PLANNED_MODELS = {"elo", "glicko", "xgboost", "lightgbm"}


@dataclass(frozen=True)
class ModelSelection:
    name: str
    description: str
    experimental: bool


MODEL_REGISTRY = {
    "vrs": ModelSelection("vrs", "Valve Regional Standings score baseline", False),
    "feature-score": ModelSelection("feature-score", "User-provided feature score column", True),
    "factor-score": ModelSelection("factor-score", "Explainable VRS + HLTV factor score", True),
    "logistic": ModelSelection("logistic", "Trained L2 logistic baseline JSON", True),
    "elo": ModelSelection("elo", "Planned Elo match-history model", True),
    "glicko": ModelSelection("glicko", "Planned Glicko uncertainty model", True),
    "catboost": ModelSelection("catboost", "Runnable CatBoost pairwise match model", True),
    "xgboost": ModelSelection("xgboost", "Planned constrained XGBoost experiment", True),
    "lightgbm": ModelSelection("lightgbm", "Planned constrained LightGBM experiment", True),
}


def resolve_model_name(model: str, snapshot: str | None, model_json: str | None) -> str:
    if model == "vrs" and (snapshot or model_json):
        return "logistic"
    return model


def apply_team_model(
    teams: list[Team],
    model: str,
    scale: float,
    snapshot: str | None = None,
    model_json: str | None = None,
    model_target: str = "advanced",
    feature_snapshot: str | None = None,
    score_column: str = "feature_score",
) -> list[Team]:
    selected_model = resolve_model_name(model, snapshot, model_json)
    if selected_model == "vrs":
        return teams
    if selected_model == "logistic":
        if not snapshot or not model_json:
            raise ValueError("--model logistic requires --snapshot and --model-json")
        return build_model_scored_teams(
            teams=teams,
            snapshot_path=snapshot,
            model_json_path=model_json,
            target=model_target,
            score_scale=scale,
        )
    if selected_model == "feature-score":
        if not feature_snapshot:
            raise ValueError("--model feature-score requires --feature-snapshot")
        return build_score_column_teams(teams, feature_snapshot, score_column, selected_model)
    if selected_model == "factor-score":
        if not feature_snapshot:
            raise ValueError("--model factor-score requires --feature-snapshot")
        factor_column = "factor_score" if score_column == "feature_score" else score_column
        return build_score_column_teams(teams, feature_snapshot, factor_column, selected_model)
    if selected_model == "catboost":
        if not feature_snapshot or not model_json:
            raise ValueError("--model catboost requires --feature-snapshot and --model-json")
        return score_teams_with_catboost(
            teams=teams,
            feature_snapshot=feature_snapshot,
            model_json=model_json,
            score_scale=scale,
        )
    if selected_model in PLANNED_MODELS:
        raise NotImplementedError(
            f"--model {selected_model} is planned but not runnable yet. "
            "It requires historical match-level feature data and validation before use."
        )
    raise ValueError(f"Unknown model: {model}")


def build_score_column_teams(
    teams: list[Team],
    feature_snapshot: str | Path,
    score_column: str,
    model_name: str,
) -> list[Team]:
    rows = load_feature_rows(feature_snapshot)
    validate_snapshot_matches_teams(teams, rows)
    row_by_team = {row["team"]: row for row in rows}
    scored_teams: list[Team] = []
    for team in teams:
        row = row_by_team[team.name]
        if score_column not in row:
            raise ValueError(f"Feature snapshot is missing score column: {score_column}")
        try:
            score = float(row[score_column])
        except ValueError as exc:
            raise ValueError(f"Feature score for {team.name} is not numeric: {row[score_column]}") from exc
        note = f"model={model_name}; score_column={score_column}; original_score={team.score:.1f}"
        scored_teams.append(
            Team(
                seed=team.seed,
                name=team.name,
                score=score,
                region=team.region,
                notes=f"{team.notes}; {note}" if team.notes else note,
            )
        )
    return scored_teams


def load_feature_rows(feature_snapshot: str | Path) -> list[dict[str, str]]:
    with Path(feature_snapshot).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        blocked = sorted(BLOCKED_FEATURE_COLUMNS & fieldnames)
        if blocked:
            raise ValueError(f"Feature snapshot contains leakage-prone columns: {', '.join(blocked)}")
        return list(reader)
