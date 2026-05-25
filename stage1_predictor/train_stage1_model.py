from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from .labels import load_label_rows, parse_bool, validate_labels
from .snapshots import validate_snapshot


TARGETS = ("advanced", "went_3_0", "went_0_3")
REGIONS = ("Americas", "Asia", "EU")


@dataclass(frozen=True)
class Example:
    event_id: str
    team: str
    features: tuple[float, ...]
    targets: dict[str, int]
    sample_weight: float


@dataclass(frozen=True)
class LogisticModel:
    weights: tuple[float, ...]

    def predict(self, features: tuple[float, ...]) -> float:
        return sigmoid(sum(weight * value for weight, value in zip(self.weights, features)))


def load_examples(snapshot_paths: list[str], label_paths: list[str]) -> list[Example]:
    labels_by_key: dict[tuple[str, str, str], dict[str, str]] = {}
    for label_path in label_paths:
        result = validate_labels(label_path)
        if not result.ok:
            raise ValueError(f"Invalid labels {label_path}: {'; '.join(result.errors)}")
        for row in load_label_rows(label_path):
            key = (row["event_id"], row["stage_id"], row["team"])
            labels_by_key[key] = row

    examples: list[Example] = []
    for snapshot_path in snapshot_paths:
        result = validate_snapshot(snapshot_path)
        if not result.ok:
            raise ValueError(f"Invalid snapshot {snapshot_path}: {'; '.join(result.errors)}")
        with Path(snapshot_path).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        examples.extend(build_examples_for_event(rows, labels_by_key))
    return examples


def build_examples_for_event(
    rows: list[dict[str, str]],
    labels_by_key: dict[tuple[str, str, str], dict[str, str]],
) -> list[Example]:
    scores = [float(row["score"]) for row in rows]
    seeds = [float(row["seed"]) for row in rows]
    score_mean = sum(scores) / len(scores)
    seed_mean = sum(seeds) / len(seeds)
    score_std = population_std(scores) or 1.0
    seed_std = population_std(seeds) or 1.0

    examples: list[Example] = []
    for row in rows:
        key = (row["event_id"], row["stage_id"], row["team"])
        if key not in labels_by_key:
            raise ValueError(f"Missing label for {key[0]} {key[1]} {key[2]}")
        label = labels_by_key[key]
        features = build_features(row, score_mean, score_std, seed_mean, seed_std)
        targets = {
            target: int(parse_bool(label[target]) is True)
            for target in TARGETS
        }
        examples.append(
            Example(
                event_id=row["event_id"],
                team=row["team"],
                features=features,
                targets=targets,
                sample_weight=float(row["sample_weight"]),
            )
        )
    return examples


def build_features(
    row: dict[str, str],
    score_mean: float,
    score_std: float,
    seed_mean: float,
    seed_std: float,
) -> tuple[float, ...]:
    score_z = (float(row["score"]) - score_mean) / score_std
    higher_seed_is_better_z = (seed_mean - float(row["seed"])) / seed_std
    region_features = tuple(1.0 if row.get("region") == region else 0.0 for region in REGIONS)
    return (1.0, score_z, higher_seed_is_better_z, *region_features)


def fit_logistic(
    examples: list[Example],
    target: str,
    l2: float,
    learning_rate: float,
    epochs: int,
) -> LogisticModel:
    if not examples:
        raise ValueError("Cannot train on zero examples")
    weights = [0.0 for _ in examples[0].features]
    total_weight = sum(example.sample_weight for example in examples) or 1.0

    for _ in range(epochs):
        gradients = [0.0 for _ in weights]
        for example in examples:
            prediction = sigmoid(sum(weight * value for weight, value in zip(weights, example.features)))
            error = prediction - example.targets[target]
            for index, value in enumerate(example.features):
                gradients[index] += example.sample_weight * error * value

        for index in range(len(weights)):
            penalty = 0.0 if index == 0 else l2 * weights[index]
            weights[index] -= learning_rate * ((gradients[index] / total_weight) + penalty)

    return LogisticModel(tuple(weights))


def evaluate_model(model: LogisticModel, examples: list[Example], target: str) -> dict[str, float]:
    if not examples:
        return {"log_loss": 0.0, "brier": 0.0, "accuracy": 0.0, "n": 0.0}
    log_loss = 0.0
    brier = 0.0
    correct = 0
    total_weight = 0.0
    prevalence = sum(example.targets[target] for example in examples) / len(examples)

    for example in examples:
        prediction = clamp_probability(model.predict(example.features))
        actual = example.targets[target]
        weight = example.sample_weight
        log_loss += weight * (-(actual * math.log(prediction) + (1 - actual) * math.log(1 - prediction)))
        brier += weight * ((prediction - actual) ** 2)
        correct += int((prediction >= prevalence) == bool(actual))
        total_weight += weight

    total_weight = total_weight or 1.0
    return {
        "log_loss": log_loss / total_weight,
        "brier": brier / total_weight,
        "accuracy": correct / len(examples),
        "n": float(len(examples)),
    }


def leave_one_event_out(
    examples: list[Example],
    l2: float,
    learning_rate: float,
    epochs: int,
) -> dict[str, object]:
    event_ids = sorted({example.event_id for example in examples})
    folds: list[dict[str, object]] = []
    for event_id in event_ids:
        train = [example for example in examples if example.event_id != event_id]
        test = [example for example in examples if example.event_id == event_id]
        if not train or not test:
            continue
        target_metrics = {}
        for target in TARGETS:
            model = fit_logistic(train, target, l2, learning_rate, epochs)
            target_metrics[target] = evaluate_model(model, test, target)
        folds.append({"test_event_id": event_id, "metrics": target_metrics})

    aggregate: dict[str, dict[str, float]] = {}
    for target in TARGETS:
        metric_names = ("log_loss", "brier", "accuracy")
        aggregate[target] = {
            metric: mean(float(fold["metrics"][target][metric]) for fold in folds) if folds else 0.0
            for metric in metric_names
        }
    return {"folds": folds, "aggregate": aggregate}


def train_final_models(
    examples: list[Example],
    l2: float,
    learning_rate: float,
    epochs: int,
) -> dict[str, dict[str, object]]:
    return {
        target: {
            "weights": list(fit_logistic(examples, target, l2, learning_rate, epochs).weights),
            "features": ["intercept", "score_z", "seed_z_higher_is_better", *[f"region_{region}" for region in REGIONS]],
        }
        for target in TARGETS
    }


def render_markdown_report(payload: dict[str, object]) -> str:
    lines = [
        "# Stage 1 Model Training Report",
        "",
        "This report uses pre-event snapshots only. Outcome labels are loaded from separate label files.",
        "",
        f"- Examples: {payload['example_count']}",
        f"- Events: {', '.join(payload['event_ids'])}",
        f"- Regularization: L2={payload['l2']}",
        "",
        "## Leave-One-Event-Out Backtest",
        "",
        "| Target | Log loss | Brier | Accuracy |",
        "|---|---:|---:|---:|",
    ]
    aggregate = payload["backtest"]["aggregate"]  # type: ignore[index]
    for target in TARGETS:
        metrics = aggregate[target]
        lines.append(
            f"| {target} | {metrics['log_loss']:.4f} | {metrics['brier']:.4f} | {metrics['accuracy']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            "Only two new-format Stage 1 historical events are available here, so the model is a leakage-safe baseline, not a stable production-calibrated estimator.",
        ]
    )
    return "\n".join(lines) + "\n"


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def clamp_probability(value: float) -> float:
    return min(max(value, 1e-6), 1 - 1e-6)


def population_std(values: list[float]) -> float:
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def mean(values: object) -> float:
    materialized = list(values)  # type: ignore[arg-type]
    return sum(materialized) / len(materialized) if materialized else 0.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train leakage-safe Stage 1 outcome models")
    parser.add_argument("--snapshots", nargs="+", required=True, help="Feature snapshot CSV paths")
    parser.add_argument("--labels", nargs="+", required=True, help="Outcome label CSV paths")
    parser.add_argument("--output-json", required=True, help="Output model/evaluation JSON path")
    parser.add_argument("--report", required=True, help="Output Markdown report path")
    parser.add_argument("--l2", type=float, default=0.20)
    parser.add_argument("--learning-rate", type=float, default=0.08)
    parser.add_argument("--epochs", type=int, default=2500)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    examples = load_examples(args.snapshots, args.labels)
    payload: dict[str, object] = {
        "example_count": len(examples),
        "event_ids": sorted({example.event_id for example in examples}),
        "targets": list(TARGETS),
        "l2": args.l2,
        "learning_rate": args.learning_rate,
        "epochs": args.epochs,
        "backtest": leave_one_event_out(examples, args.l2, args.learning_rate, args.epochs),
        "final_models": train_final_models(examples, args.l2, args.learning_rate, args.epochs),
    }

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_markdown_report(payload), encoding="utf-8")
    print(f"Wrote model report to {args.report}")
    print(f"Wrote model JSON to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
