from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from .io import validate_teams
from .labels import load_label_rows, parse_bool, validate_labels
from .models import Team
from .pickem import summarize_probabilities
from .snapshots import validate_snapshot
from .swiss import SimulationConfig, run_simulations
from .catboost_model import score_teams_with_catboost


TARGET_WEIGHTS = {"advanced": 0.50, "went_3_0": 0.25, "went_0_3": 0.25}


@dataclass(frozen=True)
class CalibrationCandidate:
    scale: float
    bo1_shrink: float
    bo3_shrink: float
    veto_weight: float = 1.0


@dataclass(frozen=True)
class CalibrationEvent:
    event_id: str
    teams: list[Team]
    labels: dict[str, dict[str, int]]


def load_events(
    snapshot_paths: list[str],
    label_paths: list[str],
    score_column: str,
    model_json: str | None = None,
    model_score_scale: float = 120.0,
) -> list[CalibrationEvent]:
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

    events: list[CalibrationEvent] = []
    for snapshot_path in snapshot_paths:
        result = validate_snapshot(snapshot_path)
        if not result.ok:
            raise ValueError(f"Invalid snapshot {snapshot_path}: {'; '.join(result.errors)}")
        with Path(snapshot_path).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise ValueError(f"Snapshot has no rows: {snapshot_path}")
        if score_column not in rows[0]:
            raise ValueError(f"Snapshot {snapshot_path} is missing score column: {score_column}")

        event_id = rows[0]["event_id"]
        teams = [
            Team(
                seed=int(row["seed"]),
                name=row["team"],
                score=float(row[score_column]),
                region=row.get("region", ""),
            )
            for row in rows
        ]
        if model_json:
            teams = score_teams_with_catboost(teams, snapshot_path, model_json, model_score_scale)
        validate_teams(teams)

        labels = labels_by_event.get(event_id)
        if labels is None:
            raise ValueError(f"Missing labels for event: {event_id}")
        missing = sorted({team.name for team in teams} - set(labels))
        if missing:
            raise ValueError(f"Labels for {event_id} are missing teams: {', '.join(missing)}")
        events.append(CalibrationEvent(event_id=event_id, teams=sorted(teams, key=lambda team: team.seed), labels=labels))
    return events


def build_candidates(
    scales: list[float],
    bo1_shrinks: list[float],
    bo3_shrinks: list[float],
    veto_weights: list[float],
) -> list[CalibrationCandidate]:
    return [
        CalibrationCandidate(scale=scale, bo1_shrink=bo1, bo3_shrink=bo3, veto_weight=veto)
        for scale in scales
        for bo1 in bo1_shrinks
        for bo3 in bo3_shrinks
        for veto in veto_weights
    ]


def evaluate_candidate(
    candidate: CalibrationCandidate,
    events: list[CalibrationEvent],
    simulations: int,
    seed: int,
) -> dict[str, float]:
    target_loss = {target: 0.0 for target in TARGET_WEIGHTS}
    target_brier = {target: 0.0 for target in TARGET_WEIGHTS}
    count = 0
    for event_index, event in enumerate(events):
        config = SimulationConfig(
            scale=candidate.scale,
            bo1_shrink=candidate.bo1_shrink,
            bo3_shrink=candidate.bo3_shrink,
            veto_weight=candidate.veto_weight,
        )
        outcomes = run_simulations(event.teams, simulations, seed + event_index * 1009, config)
        probabilities = summarize_probabilities(event.teams, outcomes)
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
    objective = sum(average_loss[target] * weight for target, weight in TARGET_WEIGHTS.items())
    brier = sum(average_brier[target] * weight for target, weight in TARGET_WEIGHTS.items())
    return {
        "objective": objective,
        "brier": brier,
        **{f"{target}_log_loss": value for target, value in average_loss.items()},
        **{f"{target}_brier": value for target, value in average_brier.items()},
    }


def tune_candidates(
    candidates: list[CalibrationCandidate],
    events: list[CalibrationEvent],
    simulations: int,
    seed: int,
) -> tuple[CalibrationCandidate, dict[str, float]]:
    scored = [
        (candidate, evaluate_candidate(candidate, events, simulations, seed))
        for candidate in candidates
    ]
    return min(scored, key=lambda item: (item[1]["objective"], item[1]["brier"], item[0].scale))


def leave_one_event_out(
    candidates: list[CalibrationCandidate],
    events: list[CalibrationEvent],
    simulations: int,
    seed: int,
) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    for event in events:
        train = [candidate_event for candidate_event in events if candidate_event.event_id != event.event_id]
        if not train:
            continue
        best, train_metrics = tune_candidates(candidates, train, simulations, seed)
        test_metrics = evaluate_candidate(best, [event], simulations, seed + 50000)
        folds.append(
            {
                "test_event_id": event.event_id,
                "selected_parameters": candidate_to_dict(best),
                "train_objective": train_metrics["objective"],
                "test_objective": test_metrics["objective"],
                "test_brier": test_metrics["brier"],
            }
        )
    return folds


def render_report(payload: dict[str, object]) -> str:
    params = payload["parameters"]  # type: ignore[assignment]
    metrics = payload["training_metrics"]  # type: ignore[assignment]
    lines = [
        "# Stage 1 BO1/BO3 校准报告",
        "",
        "这份报告用历史 Stage 1 样本微调全局概率校准层；重点是分别选择 BO1 和 BO3 的收缩参数，避免把两种赛制当成同一种不确定性。",
        "",
        "## 最终参数",
        "",
        f"- scale: `{params['scale']}`",  # type: ignore[index]
        f"- bo1_shrink: `{params['bo1_shrink']}`",  # type: ignore[index]
        f"- bo3_shrink: `{params['bo3_shrink']}`",  # type: ignore[index]
        f"- veto_weight: `{params['veto_weight']}`",  # type: ignore[index]
        "",
        "## 训练目标",
        "",
        "- advanced 权重：50%",
        "- went_3_0 权重：25%",
        "- went_0_3 权重：25%",
        "",
        "## 训练集内指标",
        "",
        f"- objective: `{metrics['objective']:.4f}`",  # type: ignore[index]
        f"- brier: `{metrics['brier']:.4f}`",  # type: ignore[index]
        f"- advanced_log_loss: `{metrics['advanced_log_loss']:.4f}`",  # type: ignore[index]
        f"- went_3_0_log_loss: `{metrics['went_3_0_log_loss']:.4f}`",  # type: ignore[index]
        f"- went_0_3_log_loss: `{metrics['went_0_3_log_loss']:.4f}`",  # type: ignore[index]
        "",
        "## Leave-One-Event-Out",
        "",
        "| 测试赛事 | 选择参数 | 测试 objective | 测试 brier |",
        "|---|---|---:|---:|",
    ]
    for fold in payload["backtest_folds"]:  # type: ignore[index]
        selected = fold["selected_parameters"]
        lines.append(
            "| {event} | scale={scale}, bo1={bo1}, bo3={bo3}, veto={veto} | {objective:.4f} | {brier:.4f} |".format(
                event=fold["test_event_id"],
                scale=selected["scale"],
                bo1=selected["bo1_shrink"],
                bo3=selected["bo3_shrink"],
                veto=selected["veto_weight"],
                objective=fold["test_objective"],
                brier=fold["test_brier"],
            )
        )
    lines.extend(
        [
            "",
            "## 重要限制",
            "",
            "当前历史样本只有两个新赛制 Stage 1，且历史 map-stats 不完整。因此这版校准主要学习 Swiss/BO1/BO3 概率尺度；`veto_weight` 保持为 1.0，用于当前赛事有地图数据时完整启用 ban/pick 修正。",
        ]
    )
    return "\n".join(lines) + "\n"


def log_loss(prediction: float, actual: int) -> float:
    value = min(1 - 1e-6, max(1e-6, prediction))
    return -(actual * math.log(value) + (1 - actual) * math.log(1 - value))


def candidate_to_dict(candidate: CalibrationCandidate) -> dict[str, float]:
    return {
        "scale": candidate.scale,
        "bo1_shrink": candidate.bo1_shrink,
        "bo3_shrink": candidate.bo3_shrink,
        "veto_weight": candidate.veto_weight,
    }


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a small factor-veto calibration layer")
    parser.add_argument("--snapshots", nargs="+", required=True, help="Historical pre-event snapshot CSV paths")
    parser.add_argument("--labels", nargs="+", required=True, help="Historical Stage 1 label CSV paths")
    parser.add_argument("--score-column", default="score", help="Snapshot score column used during calibration")
    parser.add_argument("--model-json", help="Optional CatBoost model JSON; if set, score historical snapshots with this model before tuning")
    parser.add_argument("--model-score-scale", type=float, default=120.0)
    parser.add_argument("--model-name", default="factor-veto-calibrated")
    parser.add_argument("--output-json", required=True, help="Output calibration JSON")
    parser.add_argument("--report", required=True, help="Output Markdown report")
    parser.add_argument("--simulations", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=20260524)
    parser.add_argument("--scales", default="90,105,120,135,150")
    parser.add_argument("--bo1-shrinks", default="0.55,0.65,0.70,0.75,0.85")
    parser.add_argument("--bo3-shrinks", default="0.90,1.00,1.10")
    parser.add_argument("--veto-weights", default="1.00")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    events = load_events(args.snapshots, args.labels, args.score_column, args.model_json, args.model_score_scale)
    candidates = build_candidates(
        parse_float_list(args.scales),
        parse_float_list(args.bo1_shrinks),
        parse_float_list(args.bo3_shrinks),
        parse_float_list(args.veto_weights),
    )
    best, metrics = tune_candidates(candidates, events, args.simulations, args.seed)
    payload: dict[str, object] = {
        "model": args.model_name,
        "score_column": args.score_column,
        "model_json": args.model_json or "",
        "model_score_scale": args.model_score_scale,
        "event_ids": [event.event_id for event in events],
        "simulations": args.simulations,
        "seed": args.seed,
        "objective_weights": TARGET_WEIGHTS,
        "candidate_count": len(candidates),
        "parameters": candidate_to_dict(best),
        "training_metrics": metrics,
        "backtest_folds": leave_one_event_out(candidates, events, args.simulations, args.seed),
        "limitations": [
            "Only two new-format Stage 1 events are available.",
            "Historical map veto stats are not complete, so veto_weight is fixed unless explicitly provided in the grid.",
            "Use as a small calibration layer, not as proof that factor-veto is fully trained.",
        ],
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(payload), encoding="utf-8")
    print(f"Wrote factor-veto calibration report to {args.report}")
    print(f"Wrote factor-veto calibration JSON to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
