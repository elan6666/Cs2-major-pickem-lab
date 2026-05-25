from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .factor_snapshot import build_factor_rows
from .labels import load_label_rows, parse_bool, validate_labels
from .models import Team
from .rating_system import rating_features
from .snapshots import validate_snapshot


NUMERIC_FEATURES = (
    "score_diff",
    "seed_diff_higher_is_better",
    "vrs_points_diff",
    "hltv_rating3_diff",
    "hltv_kd_diff",
    "hltv_maps_log_diff",
    "base_strength_factor_diff",
    "seed_path_factor_diff",
    "hltv_rating_factor_diff",
    "firepower_factor_diff",
    "map_pool_depth_factor_diff",
    "sample_confidence_factor_diff",
    "opponent_quality_proxy_factor_diff",
    "roster_data_factor_diff",
    "overall_factor_rating_diff",
    "glicko_mean_diff",
    "glicko_uncertainty_diff",
    "glicko_expected",
    "vrs_tier_map_strength_diff",
    "vrs_tier_map_smoothed_win_rate_diff",
    "vrs_tier_map_sample_log_diff",
    "vrs_tier_map_quality_diff",
    "vrs_tier_map_round_margin_diff",
    "vrs_tier_map_overtime_rate_diff",
    "vrs_tier_map_close_loss_rate_diff",
    "vrs_top10_map_smoothed_win_rate_diff",
    "vrs_top20_map_smoothed_win_rate_diff",
    "vrs_top30_map_smoothed_win_rate_diff",
    "vrs_top40_map_smoothed_win_rate_diff",
    "vrs_top50_map_smoothed_win_rate_diff",
    "vrs_top70_map_smoothed_win_rate_diff",
    "vrs_top100_map_smoothed_win_rate_diff",
    "vrs_top10_map_quality_diff",
    "vrs_top20_map_quality_diff",
    "vrs_top30_map_quality_diff",
    "vrs_top40_map_quality_diff",
    "vrs_top50_map_quality_diff",
    "vrs_top70_map_quality_diff",
    "vrs_top100_map_quality_diff",
    "vrs_top10_map_sample_log_diff",
    "vrs_top20_map_sample_log_diff",
    "vrs_top30_map_sample_log_diff",
    "vrs_top40_map_sample_log_diff",
    "vrs_top50_map_sample_log_diff",
    "vrs_top70_map_sample_log_diff",
    "vrs_top100_map_sample_log_diff",
    "vrs_opponent_adjusted_scoreline_quality_diff",
    "vrs_map_win_opponent_quality_diff",
    "vrs_map_win_sample_confidence_diff",
    "vrs_scoreline_sample_confidence_diff",
    "vrs_map_veto_credibility_diff",
    "vrs_map_veto_strength_diff",
    "vrs_pick_ban_opponent_pool_proxy_diff",
    "vrs_bo1_single_map_upset_risk_diff",
    "vrs_bo3_map_depth_strength_diff",
    "vrs_overtime_strong_opponent_signal_diff",
    "vrs_weak_opponent_close_penalty_diff",
    "vrs_recent_strong_opponent_score_diff",
    "vrs_expected_margin_residual_diff",
    "vrs_expected_margin_residual_confidence_diff",
    "vrs_team_volatility_diff",
    "vrs_seed_volatility_rebound_diff",
    "vrs_pick_ban_opponent_pool_edge",
    "vrs_bo1_bo3_map_depth_edge",
)

CATEGORICAL_FEATURES = (
    "team",
    "opponent",
    "region",
    "opponent_region",
    "same_region",
    "event_id",
    "format_type",
    "round_system",
)

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

VRS_TIER_FEATURE_COLUMNS = (
    "vrs_tier_map_strength",
    "vrs_tier_map_smoothed_win_rate",
    "vrs_tier_map_sample_log",
    "vrs_tier_map_quality",
    "vrs_tier_map_round_margin",
    "vrs_tier_map_overtime_rate",
    "vrs_tier_map_close_loss_rate",
    "vrs_top10_map_smoothed_win_rate",
    "vrs_top20_map_smoothed_win_rate",
    "vrs_top30_map_smoothed_win_rate",
    "vrs_top40_map_smoothed_win_rate",
    "vrs_top50_map_smoothed_win_rate",
    "vrs_top70_map_smoothed_win_rate",
    "vrs_top100_map_smoothed_win_rate",
    "vrs_top10_map_quality",
    "vrs_top20_map_quality",
    "vrs_top30_map_quality",
    "vrs_top40_map_quality",
    "vrs_top50_map_quality",
    "vrs_top70_map_quality",
    "vrs_top100_map_quality",
    "vrs_top10_map_sample_log",
    "vrs_top20_map_sample_log",
    "vrs_top30_map_sample_log",
    "vrs_top40_map_sample_log",
    "vrs_top50_map_sample_log",
    "vrs_top70_map_sample_log",
    "vrs_top100_map_sample_log",
    "vrs_opponent_adjusted_scoreline_quality",
    "vrs_map_win_opponent_quality",
    "vrs_map_win_sample_confidence",
    "vrs_scoreline_sample_confidence",
    "vrs_map_veto_credibility",
    "vrs_map_veto_strength",
    "vrs_pick_ban_opponent_pool_proxy",
    "vrs_bo1_single_map_upset_risk",
    "vrs_bo3_map_depth_strength",
    "vrs_overtime_strong_opponent_signal",
    "vrs_weak_opponent_close_penalty",
    "vrs_recent_strong_opponent_score",
    "vrs_expected_margin_residual",
    "vrs_expected_margin_residual_confidence",
    "vrs_team_volatility",
    "vrs_seed_volatility_rebound",
)

OPTIONAL_PAIRWISE_FEATURES = (
    "vrs_pick_ban_opponent_pool_edge",
    "vrs_bo1_bo3_map_depth_edge",
)

OPTIONAL_NUMERIC_FEATURES = tuple(f"{column}_diff" for column in VRS_TIER_FEATURE_COLUMNS) + OPTIONAL_PAIRWISE_FEATURES


@dataclass(frozen=True)
class PairwiseExample:
    features: dict[str, float | str]
    target: int
    weight: float


def load_feature_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Feature snapshot has no rows: {path}")
    if "factor_score" not in rows[0]:
        rows = build_factor_rows(rows)
    return rows


def load_labels(label_paths: Iterable[str | Path]) -> dict[tuple[str, str], dict[str, str]]:
    labels: dict[tuple[str, str], dict[str, str]] = {}
    for path in label_paths:
        result = validate_labels(path)
        if not result.ok:
            raise ValueError(f"Invalid labels {path}: {'; '.join(result.errors)}")
        for row in load_label_rows(path):
            labels[(row["event_id"], row["team"])] = row
    return labels


def build_pairwise_examples(snapshot_paths: list[str], label_paths: list[str]) -> list[PairwiseExample]:
    labels = load_labels(label_paths)
    examples: list[PairwiseExample] = []
    for snapshot_path in snapshot_paths:
        result = validate_snapshot(snapshot_path)
        if not result.ok:
            raise ValueError(f"Invalid snapshot {snapshot_path}: {'; '.join(result.errors)}")
        rows = load_feature_rows(snapshot_path)
        event_id = rows[0]["event_id"]
        event_labels = {team: label for (label_event, team), label in labels.items() if label_event == event_id}
        missing = sorted({row["team"] for row in rows} - set(event_labels))
        if missing:
            raise ValueError(f"Labels for {event_id} are missing teams: {', '.join(missing)}")
        for left in rows:
            for right in rows:
                if left["team"] == right["team"]:
                    continue
                left_rank = final_record_rank(event_labels[left["team"]]["final_record"])
                right_rank = final_record_rank(event_labels[right["team"]]["final_record"])
                if left_rank == right_rank:
                    continue
                target = int(left_rank > right_rank)
                weight = abs(left_rank - right_rank) / 5.0
                examples.append(PairwiseExample(build_pair_features(left, right), target, max(0.2, weight)))
    return examples


def load_pretrain_examples(path: str | Path) -> list[PairwiseExample]:
    examples: list[PairwiseExample] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = (set(FEATURES) - set(OPTIONAL_NUMERIC_FEATURES)) | {"target"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Pretrain match/map CSV is missing columns: {', '.join(missing)}")
        for row in reader:
            features: dict[str, float | str] = {}
            for name in NUMERIC_FEATURES:
                features[name] = number(row, name, 0.0)
            for name in CATEGORICAL_FEATURES:
                features[name] = row.get(name, "")
            examples.append(
                PairwiseExample(
                    features=features,
                    target=parse_target(row["target"]),
                    weight=number(row, "sample_weight", 1.0),
                )
            )
    return examples


def final_record_rank(record: str) -> int:
    try:
        wins, losses = (int(part) for part in record.split("-", 1))
    except ValueError as exc:
        raise ValueError(f"Invalid final record: {record}") from exc
    return wins * 2 - losses


def parse_target(value: str) -> int:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "win", "won"}:
        return 1
    if lowered in {"0", "false", "no", "loss", "lost"}:
        return 0
    raise ValueError(f"Invalid target value: {value}")


def build_pair_features(left: dict[str, str], right: dict[str, str]) -> dict[str, float | str]:
    features: dict[str, float | str] = {
        "team": left["team"],
        "opponent": right["team"],
        "region": left.get("region", ""),
        "opponent_region": right.get("region", ""),
        "same_region": str(left.get("region", "") == right.get("region", "")),
        "event_id": left.get("event_id", ""),
        "format_type": left.get("format_type", ""),
        "round_system": left.get("round_system", ""),
        "score_diff": number(left, "score") - number(right, "score"),
        "seed_diff_higher_is_better": number(right, "seed", 16.0) - number(left, "seed", 16.0),
        "vrs_points_diff": number(left, "vrs_points", number(left, "score")) - number(right, "vrs_points", number(right, "score")),
        "hltv_rating3_diff": number(left, "hltv_rating3", 1.0) - number(right, "hltv_rating3", 1.0),
        "hltv_kd_diff": number(left, "hltv_kd", 1.0) - number(right, "hltv_kd", 1.0),
        "hltv_maps_log_diff": math.log1p(number(left, "hltv_maps")) - math.log1p(number(right, "hltv_maps")),
    }
    for column in (
        "base_strength_factor",
        "seed_path_factor",
        "hltv_rating_factor",
        "firepower_factor",
        "map_pool_depth_factor",
        "sample_confidence_factor",
        "opponent_quality_proxy_factor",
        "roster_data_factor",
        "overall_factor_rating",
    ):
        features[f"{column}_diff"] = number(left, column, 50.0) - number(right, column, 50.0)
    for column in VRS_TIER_FEATURE_COLUMNS:
        features[f"{column}_diff"] = number(left, column, vrs_feature_default(column)) - number(right, column, vrs_feature_default(column))
    left_veto_strength = number(left, "vrs_map_veto_strength", number(left, "vrs_tier_map_strength", 50.0))
    right_veto_strength = number(right, "vrs_map_veto_strength", number(right, "vrs_tier_map_strength", 50.0))
    left_veto_credibility = number(left, "vrs_map_veto_credibility", 0.0)
    right_veto_credibility = number(right, "vrs_map_veto_credibility", 0.0)
    strength_edge = (left_veto_strength - right_veto_strength) / 50.0
    features["vrs_pick_ban_opponent_pool_edge"] = strength_edge * (0.5 + left_veto_credibility + right_veto_credibility * 0.5)
    bo3_depth_edge = number(left, "vrs_bo3_map_depth_strength", 0.0) - number(right, "vrs_bo3_map_depth_strength", 0.0)
    bo1_risk_edge = number(left, "vrs_bo1_single_map_upset_risk", 0.0) - number(right, "vrs_bo1_single_map_upset_risk", 0.0)
    features["vrs_bo1_bo3_map_depth_edge"] = bo3_depth_edge - bo1_risk_edge * 0.5
    features.update(rating_features(left, right))
    return {name: features[name] for name in FEATURES}


def train_catboost_model(
    examples: list[PairwiseExample],
    model_path: str | Path,
    iterations: int = 120,
    depth: int = 3,
    learning_rate: float = 0.05,
    l2_leaf_reg: float = 8.0,
    use_directional_constraints: bool = False,
) -> dict[str, object]:
    if not examples:
        raise ValueError("Cannot train CatBoost on zero examples")
    try:
        from catboost import CatBoostClassifier, Pool
    except ImportError as exc:
        raise RuntimeError("CatBoost is not installed. Run `python -m pip install catboost`.") from exc

    rows = [[example.features[name] for name in FEATURES] for example in examples]
    labels = [example.target for example in examples]
    weights = [example.weight for example in examples]
    cat_indexes = [FEATURES.index(name) for name in CATEGORICAL_FEATURES]
    params = {
        "iterations": iterations,
        "depth": depth,
        "learning_rate": learning_rate,
        "l2_leaf_reg": l2_leaf_reg,
        "loss_function": "Logloss",
        "eval_metric": "BrierScore",
        "random_seed": 42,
        "verbose": False,
        "allow_writing_files": False,
    }
    if use_directional_constraints:
        params["monotone_constraints"] = directional_monotone_constraints()
    model = CatBoostClassifier(**params)
    model.fit(Pool(rows, label=labels, weight=weights, cat_features=cat_indexes))
    output = Path(model_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(output))
    return {
        "model_path": str(output),
        "features": list(FEATURES),
        "categorical_features": list(CATEGORICAL_FEATURES),
        "example_count": len(examples),
        "positive_rate": sum(labels) / len(labels),
        "params": {
            "iterations": iterations,
            "depth": depth,
            "learning_rate": learning_rate,
            "l2_leaf_reg": l2_leaf_reg,
            "use_directional_constraints": use_directional_constraints,
        },
    }


def directional_monotone_constraints() -> list[int]:
    positive = {
        "score_diff",
        "seed_diff_higher_is_better",
        "vrs_points_diff",
        "hltv_rating3_diff",
        "hltv_kd_diff",
        "hltv_maps_log_diff",
        "base_strength_factor_diff",
        "seed_path_factor_diff",
        "hltv_rating_factor_diff",
        "firepower_factor_diff",
        "map_pool_depth_factor_diff",
        "sample_confidence_factor_diff",
        "opponent_quality_proxy_factor_diff",
        "roster_data_factor_diff",
        "overall_factor_rating_diff",
        "glicko_mean_diff",
        "glicko_expected",
        "vrs_tier_map_strength_diff",
        "vrs_tier_map_smoothed_win_rate_diff",
        "vrs_tier_map_sample_log_diff",
        "vrs_tier_map_quality_diff",
        "vrs_tier_map_round_margin_diff",
        "vrs_tier_map_overtime_rate_diff",
        "vrs_top10_map_smoothed_win_rate_diff",
        "vrs_top20_map_smoothed_win_rate_diff",
        "vrs_top30_map_smoothed_win_rate_diff",
        "vrs_top40_map_smoothed_win_rate_diff",
        "vrs_top50_map_smoothed_win_rate_diff",
        "vrs_top70_map_smoothed_win_rate_diff",
        "vrs_top100_map_smoothed_win_rate_diff",
        "vrs_top10_map_quality_diff",
        "vrs_top20_map_quality_diff",
        "vrs_top30_map_quality_diff",
        "vrs_top40_map_quality_diff",
        "vrs_top50_map_quality_diff",
        "vrs_top70_map_quality_diff",
        "vrs_top100_map_quality_diff",
        "vrs_top10_map_sample_log_diff",
        "vrs_top20_map_sample_log_diff",
        "vrs_top30_map_sample_log_diff",
        "vrs_top40_map_sample_log_diff",
        "vrs_top50_map_sample_log_diff",
        "vrs_top70_map_sample_log_diff",
        "vrs_top100_map_sample_log_diff",
        "vrs_opponent_adjusted_scoreline_quality_diff",
        "vrs_map_win_opponent_quality_diff",
        "vrs_map_win_sample_confidence_diff",
        "vrs_scoreline_sample_confidence_diff",
        "vrs_map_veto_credibility_diff",
        "vrs_map_veto_strength_diff",
        "vrs_pick_ban_opponent_pool_proxy_diff",
        "vrs_bo3_map_depth_strength_diff",
        "vrs_overtime_strong_opponent_signal_diff",
        "vrs_recent_strong_opponent_score_diff",
        "vrs_expected_margin_residual_diff",
        "vrs_expected_margin_residual_confidence_diff",
        "vrs_seed_volatility_rebound_diff",
        "vrs_pick_ban_opponent_pool_edge",
        "vrs_bo1_bo3_map_depth_edge",
    }
    negative = {
        "glicko_uncertainty_diff",
        "vrs_tier_map_close_loss_rate_diff",
        "vrs_bo1_single_map_upset_risk_diff",
        "vrs_weak_opponent_close_penalty_diff",
        "vrs_team_volatility_diff",
    }
    constraints: list[int] = []
    for feature in FEATURES:
        if feature in positive:
            constraints.append(1)
        elif feature in negative:
            constraints.append(-1)
        else:
            constraints.append(0)
    return constraints


def score_teams_with_catboost(
    teams: list[Team],
    feature_snapshot: str | Path,
    model_json: str | Path,
    score_scale: float,
) -> list[Team]:
    try:
        from catboost import CatBoostClassifier, Pool
    except ImportError as exc:
        raise RuntimeError("CatBoost is not installed. Run `python -m pip install catboost`.") from exc

    metadata = json.loads(Path(model_json).read_text(encoding="utf-8"))
    model_path = resolve_model_path(metadata["model_path"], Path(model_json))
    rows = load_feature_rows(feature_snapshot)
    row_by_team = {row["team"]: row for row in rows}
    missing = sorted({team.name for team in teams} - set(row_by_team))
    if missing:
        raise ValueError(f"Feature snapshot is missing teams: {', '.join(missing)}")
    model = CatBoostClassifier()
    model.load_model(str(model_path))
    feature_names = tuple(metadata.get("features", FEATURES))
    categorical_names = tuple(metadata.get("categorical_features", CATEGORICAL_FEATURES))
    cat_indexes = [feature_names.index(name) for name in categorical_names if name in feature_names]

    scored: list[Team] = []
    for team in teams:
        logits: list[float] = []
        for opponent in teams:
            if team.name == opponent.name:
                continue
            features = build_pair_features(row_by_team[team.name], row_by_team[opponent.name])
            matrix = [[features.get(name, feature_default(name)) for name in feature_names]]
            probability = model.predict_proba(Pool(matrix, cat_features=cat_indexes))[0][1]
            logits.append(logit(float(probability)))
        average_logit = sum(logits) / len(logits)
        score = average_logit * score_scale
        notes = append_note(team.notes, f"model=catboost; pairwise_avg_logit={average_logit:.4f}")
        scored.append(Team(seed=team.seed, name=team.name, score=score, region=team.region, notes=notes))
    return scored


def number(row: dict[str, str], field: str, default: float = 0.0) -> float:
    value = row.get(field, "")
    if value is None or str(value).strip() == "":
        return default
    return float(str(value).strip())


def vrs_feature_default(column: str) -> float:
    if column.endswith("_win_rate") or column.endswith("_strength"):
        return 50.0
    return 0.0


def feature_default(name: str) -> float | str:
    if name in CATEGORICAL_FEATURES:
        return ""
    if name.endswith("_diff") and name[:-5] in VRS_TIER_FEATURE_COLUMNS:
        return 0.0
    return 0.0


def logit(value: float) -> float:
    value = min(1.0 - 1e-6, max(1e-6, value))
    return math.log(value / (1.0 - value))


def append_note(existing: str, note: str) -> str:
    if not existing:
        return note
    return f"{existing}; {note}"


def resolve_model_path(value: str, metadata_path: Path) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    relative_to_metadata = metadata_path.parent / path
    if relative_to_metadata.exists():
        return relative_to_metadata
    return path
