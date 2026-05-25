from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from .calibration import CalibrationParams, load_calibration_params
from .factor_snapshot import FACTOR_WEIGHTS, build_factor_rows, normalize_factor_weights
from .io import validate_teams
from .labels import load_label_rows, parse_bool, validate_labels
from .models import Team
from .pickem import summarize_probabilities
from .snapshots import validate_snapshot
from .swiss import SimulationConfig, run_simulations


TARGET_WEIGHTS = {"advanced": 0.50, "went_3_0": 0.25, "went_0_3": 0.25}
FACTOR_COLUMNS = tuple(FACTOR_WEIGHTS)


@dataclass(frozen=True)
class FactorWeightEvent:
    event_id: str
    rows: list[dict[str, str]]
    labels: dict[str, dict[str, int]]


def load_events(snapshot_paths: list[str], label_paths: list[str]) -> list[FactorWeightEvent]:
    labels_by_event: dict[str, dict[str, dict[str, int]]] = {}
    for label_path in label_paths:
        result = validate_labels(label_path)
        if not result.ok:
            raise ValueError(f"Invalid labels {label_path}: {'; '.join(result.errors)}")
        for row in load_label_rows(label_path):
            labels_by_event.setdefault(row["event_id"], {})[row["team"]] = {
                target: int(parse_bool(row[target]) is True)
                for target in TARGET_WEIGHTS
            }

    events: list[FactorWeightEvent] = []
    for snapshot_path in snapshot_paths:
        result = validate_snapshot(snapshot_path)
        if not result.ok:
            raise ValueError(f"Invalid snapshot {snapshot_path}: {'; '.join(result.errors)}")
        with Path(snapshot_path).open(newline="", encoding="utf-8") as handle:
            raw_rows = list(csv.DictReader(handle))
        if not raw_rows:
            raise ValueError(f"Snapshot has no rows: {snapshot_path}")
        factor_rows = build_factor_rows(raw_rows)
        event_id = factor_rows[0]["event_id"]
        labels = labels_by_event.get(event_id)
        if labels is None:
            raise ValueError(f"Missing labels for event: {event_id}")
        missing = sorted({row["team"] for row in factor_rows} - set(labels))
        if missing:
            raise ValueError(f"Labels for {event_id} are missing teams: {', '.join(missing)}")
        events.append(FactorWeightEvent(event_id=event_id, rows=factor_rows, labels=labels))
    return events


def teams_from_weighted_rows(rows: list[dict[str, str]], weights: dict[str, float]) -> list[Team]:
    teams = [
        Team(
            seed=int(row["seed"]),
            name=row["team"],
            score=factor_score(row, weights),
            region=row.get("region", ""),
        )
        for row in rows
    ]
    validate_teams(teams)
    return sorted(teams, key=lambda team: team.seed)


def factor_score(row: dict[str, str], weights: dict[str, float]) -> float:
    active_weights = normalize_factor_weights(weights)
    overall = sum(float(row[name]) * active_weights[name] for name in FACTOR_COLUMNS)
    return 1250.0 + overall * 4.2


def evaluate_weights(
    weights: dict[str, float],
    events: list[FactorWeightEvent],
    config: SimulationConfig,
    simulations: int,
    seed: int,
    regularization: float,
) -> dict[str, float]:
    active_weights = normalize_factor_weights(weights)
    target_loss = {target: 0.0 for target in TARGET_WEIGHTS}
    target_brier = {target: 0.0 for target in TARGET_WEIGHTS}
    count = 0
    for event_index, event in enumerate(events):
        teams = teams_from_weighted_rows(event.rows, active_weights)
        outcomes = run_simulations(teams, simulations, seed + event_index * 1009, config)
        probabilities = summarize_probabilities(teams, outcomes)
        for item in probabilities:
            labels = event.labels[item.team.name]
            predictions = {
                "advanced": item.advance_probability,
                "went_3_0": item.record_probabilities["3-0"],
                "went_0_3": item.record_probabilities["0-3"],
            }
            for target, prediction in predictions.items():
                actual = labels[target]
                target_loss[target] += log_loss(prediction, actual)
                target_brier[target] += (prediction - actual) ** 2
            count += 1
    count = count or 1
    average_loss = {target: target_loss[target] / count for target in TARGET_WEIGHTS}
    average_brier = {target: target_brier[target] / count for target in TARGET_WEIGHTS}
    unregularized = sum(average_loss[target] * weight for target, weight in TARGET_WEIGHTS.items())
    penalty = regularization_penalty(active_weights) * regularization
    brier = sum(average_brier[target] * weight for target, weight in TARGET_WEIGHTS.items())
    return {
        "objective": unregularized + penalty,
        "unregularized_objective": unregularized,
        "regularization_penalty": penalty,
        "brier": brier,
        **{f"{target}_log_loss": value for target, value in average_loss.items()},
        **{f"{target}_brier": value for target, value in average_brier.items()},
    }


def tune_weights(
    events: list[FactorWeightEvent],
    config: SimulationConfig,
    simulations: int,
    seed: int,
    regularization: float,
    rounds: int,
    step_sizes: list[float],
) -> tuple[dict[str, float], dict[str, float], list[dict[str, object]]]:
    current = normalize_factor_weights(FACTOR_WEIGHTS)
    current_metrics = evaluate_weights(current, events, config, simulations, seed, regularization)
    trace = [{"round": 0, "weights": current, "metrics": current_metrics}]
    for round_index in range(1, rounds + 1):
        best_weights = current
        best_metrics = current_metrics
        for candidate in candidate_neighbors(current, step_sizes):
            metrics = evaluate_weights(candidate, events, config, simulations, seed + round_index * 5000, regularization)
            if is_better(metrics, best_metrics):
                best_weights = candidate
                best_metrics = metrics
        current = best_weights
        current_metrics = best_metrics
        trace.append({"round": round_index, "weights": current, "metrics": current_metrics})
    return current, current_metrics, trace


def candidate_neighbors(weights: dict[str, float], step_sizes: list[float]) -> list[dict[str, float]]:
    candidates: list[dict[str, float]] = [weights]
    names = list(FACTOR_COLUMNS)
    for step in step_sizes:
        for source in names:
            for target in names:
                if source == target:
                    continue
                if weights[source] <= step:
                    continue
                candidate = dict(weights)
                candidate[source] -= step
                candidate[target] += step
                candidates.append(normalize_factor_weights(candidate))
    return candidates


def is_better(left: dict[str, float], right: dict[str, float]) -> bool:
    return (left["objective"], left["brier"]) < (right["objective"], right["brier"])


def regularization_penalty(weights: dict[str, float]) -> float:
    return sum((weights[name] - FACTOR_WEIGHTS[name]) ** 2 / max(FACTOR_WEIGHTS[name], 0.01) for name in FACTOR_COLUMNS)


def feature_variation(events: list[FactorWeightEvent]) -> dict[str, float]:
    values = {name: [] for name in FACTOR_COLUMNS}
    for event in events:
        for row in event.rows:
            for name in FACTOR_COLUMNS:
                values[name].append(float(row[name]))
    return {name: population_std(values[name]) for name in FACTOR_COLUMNS}


def leave_one_event_out(
    events: list[FactorWeightEvent],
    config: SimulationConfig,
    simulations: int,
    seed: int,
    regularization: float,
    rounds: int,
    step_sizes: list[float],
) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    for event in events:
        train = [candidate_event for candidate_event in events if candidate_event.event_id != event.event_id]
        if not train:
            continue
        weights, train_metrics, _ = tune_weights(train, config, simulations, seed, regularization, rounds, step_sizes)
        test_metrics = evaluate_weights(weights, [event], config, simulations, seed + 70000, regularization)
        folds.append(
            {
                "test_event_id": event.event_id,
                "selected_weights": weights,
                "train_objective": train_metrics["objective"],
                "test_objective": test_metrics["objective"],
                "test_brier": test_metrics["brier"],
            }
        )
    return folds


def build_simulation_config(calibration: CalibrationParams | None) -> SimulationConfig:
    if calibration is None:
        return SimulationConfig()
    return SimulationConfig(
        scale=calibration.scale,
        bo1_shrink=calibration.bo1_shrink,
        bo3_shrink=calibration.bo3_shrink,
        veto_weight=calibration.veto_weight,
    )


def render_report(payload: dict[str, object]) -> str:
    weights = payload["weights"]  # type: ignore[assignment]
    prior = payload["prior_weights"]  # type: ignore[assignment]
    metrics = payload["training_metrics"]  # type: ignore[assignment]
    variation = payload["historical_factor_std"]  # type: ignore[assignment]
    lines = [
        "# Factor 权重训练报告",
        "",
        "这份报告训练 `factor_score` 的 8 个因素权重。训练受到人工先验正则约束，避免两个历史 Stage 1 小样本把权重推到极端。",
        "",
        "## 最终权重",
        "",
        "| 因素 | 初始权重 | 训练权重 | 历史样本标准差 | 说明 |",
        "|---|---:|---:|---:|---|",
    ]
    explanations = {
        "base_strength_factor": "基础实力/VRS",
        "hltv_rating_factor": "HLTV rating",
        "firepower_factor": "火力/KD",
        "map_pool_depth_factor": "地图样本深度",
        "sample_confidence_factor": "样本置信度",
        "opponent_quality_proxy_factor": "对手质量代理",
        "roster_data_factor": "阵容数据可得性",
        "seed_path_factor": "种子路径",
    }
    for name in FACTOR_COLUMNS:
        note = "历史样本可区分" if variation[name] > 1e-6 else "历史样本无有效变化，主要由先验保留"
        lines.append(
            f"| {explanations[name]} | {prior[name]:.1%} | {weights[name]:.1%} | {variation[name]:.2f} | {note} |"
        )
    lines.extend(
        [
            "",
            "## 训练指标",
            "",
            f"- objective: `{metrics['objective']:.4f}`",
            f"- unregularized_objective: `{metrics['unregularized_objective']:.4f}`",
            f"- regularization_penalty: `{metrics['regularization_penalty']:.4f}`",
            f"- brier: `{metrics['brier']:.4f}`",
            f"- advanced_log_loss: `{metrics['advanced_log_loss']:.4f}`",
            f"- went_3_0_log_loss: `{metrics['went_3_0_log_loss']:.4f}`",
            f"- went_0_3_log_loss: `{metrics['went_0_3_log_loss']:.4f}`",
            "",
            "## Leave-One-Event-Out",
            "",
            "| 测试赛事 | 测试 objective | 测试 brier |",
            "|---|---:|---:|",
        ]
    )
    for fold in payload["backtest_folds"]:  # type: ignore[index]
        lines.append(f"| {fold['test_event_id']} | {fold['test_objective']:.4f} | {fold['test_brier']:.4f} |")
    lines.extend(
        [
            "",
            "## 重要限制",
            "",
            "Austin/Budapest 历史快照没有完整 HLTV rating、K/D、地图样本深度和当前阵容来源字段，因此这些维度在历史训练里可识别性有限。训练器仍会输出 8 个权重，但必须把它看作“受约束微调”，不是大样本充分学习。",
        ]
    )
    return "\n".join(lines) + "\n"


def log_loss(prediction: float, actual: int) -> float:
    value = min(1 - 1e-6, max(1e-6, prediction))
    return -(actual * math.log(value) + (1 - actual) * math.log(1 - value))


def population_std(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train constrained factor-score weights")
    parser.add_argument("--snapshots", nargs="+", required=True, help="Historical pre-event snapshot CSV paths")
    parser.add_argument("--labels", nargs="+", required=True, help="Historical Stage 1 label CSV paths")
    parser.add_argument("--calibration-json", help="Optional probability calibration JSON")
    parser.add_argument("--output-json", required=True, help="Output trained weights JSON")
    parser.add_argument("--report", required=True, help="Output Markdown report")
    parser.add_argument("--simulations", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=20260524)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--step-sizes", default="0.04,0.02")
    parser.add_argument("--regularization", type=float, default=0.08)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    events = load_events(args.snapshots, args.labels)
    calibration = load_calibration_params(args.calibration_json) if args.calibration_json else None
    config = build_simulation_config(calibration)
    step_sizes = parse_float_list(args.step_sizes)
    weights, metrics, trace = tune_weights(
        events=events,
        config=config,
        simulations=args.simulations,
        seed=args.seed,
        regularization=args.regularization,
        rounds=args.rounds,
        step_sizes=step_sizes,
    )
    payload: dict[str, object] = {
        "model": "factor-weight-veto-calibrated",
        "weights": weights,
        "prior_weights": FACTOR_WEIGHTS,
        "event_ids": [event.event_id for event in events],
        "simulations": args.simulations,
        "seed": args.seed,
        "rounds": args.rounds,
        "step_sizes": step_sizes,
        "regularization": args.regularization,
        "calibration_json": args.calibration_json or "",
        "simulation_config": {
            "scale": config.scale,
            "bo1_shrink": config.bo1_shrink,
            "bo3_shrink": config.bo3_shrink,
            "veto_weight": config.veto_weight,
        },
        "training_metrics": metrics,
        "historical_factor_std": feature_variation(events),
        "trace": trace,
        "backtest_folds": leave_one_event_out(
            events=events,
            config=config,
            simulations=args.simulations,
            seed=args.seed,
            regularization=args.regularization,
            rounds=args.rounds,
            step_sizes=step_sizes,
        ),
        "limitations": [
            "Only two new-format Stage 1 events are available.",
            "Historical snapshots do not include full HLTV/KD/map-depth/current-roster fields, so some factor weights are weakly identifiable.",
            "Weights are constrained by a prior regularization term and should remain experimental.",
        ],
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(payload), encoding="utf-8")
    print(f"Wrote factor weight training report to {args.report}")
    print(f"Wrote factor weight JSON to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
