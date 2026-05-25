from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .labels import load_label_rows, parse_bool


def parse_named_path(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected NAME=path")
    name, path = value.split("=", 1)
    if not name or not path:
        raise argparse.ArgumentTypeError("Expected NAME=path")
    return name, path


def parse_history_arg(value: str) -> tuple[str, str, str]:
    if "=" not in value or "," not in value:
        raise argparse.ArgumentTypeError("Expected NAME=prediction_json,labels_csv")
    name, rest = value.split("=", 1)
    prediction_json, labels_csv = rest.split(",", 1)
    if not name or not prediction_json or not labels_csv:
        raise argparse.ArgumentTypeError("Expected NAME=prediction_json,labels_csv")
    return name, prediction_json, labels_csv


def parse_percent(value: object) -> float:
    text = str(value).strip()
    if text.endswith("%"):
        return float(text[:-1]) / 100.0
    return float(text)


def load_current_summary(path: str | Path) -> dict[str, float]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    card = payload["pickem_card"]
    return {
        "pass_probability": float(card["pass_probability"]),
        "expected_correct": float(card["expected_correct"]),
    }


def evaluate_history(prediction_json: str | Path, labels_csv: str | Path) -> dict[str, float]:
    predictions = json.loads(Path(prediction_json).read_text(encoding="utf-8"))
    probabilities = {
        str(row["team"]).strip(): parse_percent(row["p_advance"])
        for row in predictions.get("probabilities", [])
    }
    labels: dict[str, bool] = {}
    for row in load_label_rows(labels_csv):
        parsed = parse_bool(row.get("advanced", ""))
        if parsed is None:
            raise ValueError(f"Invalid advanced label for {row.get('team', '')} in {labels_csv}")
        labels[row["team"].strip()] = parsed

    missing = sorted(set(labels) - set(probabilities))
    if missing:
        raise ValueError(f"Prediction file {prediction_json} is missing teams: {', '.join(missing)}")

    brier_terms: list[float] = []
    log_loss_terms: list[float] = []
    correct = 0
    for team, advanced in labels.items():
        probability = min(max(probabilities[team], 1e-6), 1.0 - 1e-6)
        target = 1.0 if advanced else 0.0
        brier_terms.append((probability - target) ** 2)
        log_loss_terms.append(-(target * math.log(probability) + (1.0 - target) * math.log(1.0 - probability)))
        correct += int((probability >= 0.5) == advanced)

    count = len(labels)
    return {
        "team_count": float(count),
        "brier_score": sum(brier_terms) / count,
        "log_loss": sum(log_loss_terms) / count,
        "advance_accuracy": correct / count,
    }


def weighted_average(rows: list[dict[str, float]], key: str) -> float:
    total_weight = sum(row["team_count"] for row in rows)
    if total_weight == 0:
        return 0.0
    return sum(row[key] * row["team_count"] for row in rows) / total_weight


def build_rows(
    summaries: list[tuple[str, str]],
    histories: list[tuple[str, str, str]],
) -> list[dict[str, object]]:
    summary_by_model = {name: load_current_summary(path) for name, path in summaries}
    history_by_model: dict[str, list[dict[str, float]]] = {}
    for name, prediction_json, labels_csv in histories:
        history_by_model.setdefault(name, []).append(evaluate_history(prediction_json, labels_csv))

    rows: list[dict[str, object]] = []
    for name in sorted(summary_by_model):
        history_rows = history_by_model.get(name, [])
        current = summary_by_model[name]
        rows.append(
            {
                "model": name,
                "pass_probability": current["pass_probability"],
                "expected_correct": current["expected_correct"],
                "brier_score": weighted_average(history_rows, "brier_score") if history_rows else None,
                "log_loss": weighted_average(history_rows, "log_loss") if history_rows else None,
                "advance_accuracy": weighted_average(history_rows, "advance_accuracy") if history_rows else None,
                "history_events": len(history_rows),
                "history_teams": int(sum(row["team_count"] for row in history_rows)),
            }
        )
    return sorted(rows, key=lambda row: (-float(row["pass_probability"]), str(row["model"])))


def render_value(value: object, kind: str) -> str:
    if value is None:
        return "n/a"
    if kind == "percent":
        return f"{float(value):.1%}"
    return f"{float(value):.4f}"


def render_report(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Stage 1 加权重训评估",
        "",
        "| 模型 | Pick'Em 通过率 | 期望猜中 | Brier 分数 | 对数损失 | 晋级命中率 | 历史事件 | 历史队伍 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {model} | {pass_probability} | {expected_correct:.2f} | {brier_score} | {log_loss} | {advance_accuracy} | {history_events} | {history_teams} |".format(
                model=row["model"],
                pass_probability=render_value(row["pass_probability"], "percent"),
                expected_correct=float(row["expected_correct"]),
                brier_score=render_value(row["brier_score"], "float"),
                log_loss=render_value(row["log_loss"], "float"),
                advance_accuracy=render_value(row["advance_accuracy"], "percent"),
                history_events=row["history_events"],
                history_teams=row["history_teams"],
            )
        )
    lines.extend(
        [
            "",
            "## 口径",
            "",
            "Pick'Em 通过率和期望猜中来自当前 Cologne Stage 1 模拟；Brier 分数、对数损失、晋级命中率来自 Austin 2025 Stage 1 与 Budapest 2025 Stage 1 的赛前预测对最终晋级标签回测。",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate current Pick'Em summaries and historical advance-label metrics")
    parser.add_argument("--summary", action="append", required=True, type=parse_named_path, help="Current model summary in NAME=path form")
    parser.add_argument("--history", action="append", default=[], type=parse_history_arg, help="Historical pair in NAME=prediction_json,labels_csv form")
    parser.add_argument("--report", required=True)
    parser.add_argument("--json", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = build_rows(args.summary, args.history)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(rows), encoding="utf-8")
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps({"models": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote evaluation report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
