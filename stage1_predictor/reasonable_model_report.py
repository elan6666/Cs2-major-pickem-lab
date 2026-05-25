from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .evaluate_prediction_metrics import evaluate_history, load_current_summary


POSITIVE_SIGNALS = {
    "vrs_map_win_opponent_quality": "地图胜率来自更强对手",
    "vrs_recent_strong_opponent_score": "近期强队表现",
    "vrs_expected_margin_residual_confidence": "比分超出预期且有样本",
    "vrs_bo3_map_depth_strength": "BO3 地图深度",
    "vrs_map_veto_strength": "veto 可信地图强度",
    "vrs_scoreline_sample_confidence": "比分质量样本置信",
    "vrs_opponent_adjusted_scoreline_quality": "对手强度调整比分质量",
}

NEGATIVE_SIGNALS = {
    "vrs_weak_opponent_close_penalty": "弱队近比分惩罚",
    "vrs_bo1_single_map_upset_risk": "BO1 单图波动",
    "vrs_team_volatility": "队伍比分波动",
    "vrs_tier_map_close_loss_rate": "地图惜败率",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a reasonableness, overfit, uncertainty, and team explanation report")
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--current-json", required=True)
    parser.add_argument("--austin-json", required=True)
    parser.add_argument("--austin-labels", required=True)
    parser.add_argument("--budapest-json", required=True)
    parser.add_argument("--budapest-labels", required=True)
    parser.add_argument("--feature-snapshot", required=True)
    parser.add_argument("--model-json", required=True)
    parser.add_argument("--pretrain-csv", required=True)
    parser.add_argument("--calibration-json", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--json", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = build_payload(args)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(payload), encoding="utf-8")
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote reasonableness report to {args.report}")
    return 0


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    current = load_prediction(args.current_json)
    current_settings = current.get("settings", {})
    austin_summary = load_current_summary(args.austin_json)
    budapest_summary = load_current_summary(args.budapest_json)
    austin_history = evaluate_history(args.austin_json, args.austin_labels)
    budapest_history = evaluate_history(args.budapest_json, args.budapest_labels)
    combined = combine_history([austin_history, budapest_history])
    model = json.loads(Path(args.model_json).read_text(encoding="utf-8"))
    calibration = json.loads(Path(args.calibration_json).read_text(encoding="utf-8"))
    snapshot_rows = load_rows(args.feature_snapshot)
    pretrain_columns = csv_columns(args.pretrain_csv)
    return {
        "model": args.model_name,
        "current": {
            **load_current_summary(args.current_json),
            "pickem_card": current["pickem_card"],
            "uncertainty": uncertainty_rows(current),
        },
        "overfit_evaluation": {
            "austin": {**austin_summary, **austin_history},
            "budapest": {**budapest_summary, **budapest_history},
            "combined": combined,
        },
        "direction_constraints": {
            "enabled": bool(model.get("params", {}).get("use_directional_constraints")),
            "checked_positive_signals": sorted(POSITIVE_SIGNALS),
            "checked_negative_signals": sorted(NEGATIVE_SIGNALS),
        },
        "temporal_vrs": {
            "vrs_files": sorted(path.name for path in Path("data/vrs").glob("standings_global_2026_*.md")),
            "snapshot_has_expected_residual": has_nonzero(snapshot_rows, "vrs_expected_margin_residual"),
            "pretrain_has_expected_residual_diff": "vrs_expected_margin_residual_diff" in pretrain_columns,
        },
        "bo1_bo3_calibration": calibration.get("parameters", {}),
        "veto_counter_simulation": {
            "enabled": bool(current_settings.get("map_stats") and current_settings.get("veto_policy") == "contextual-bandit"),
            "veto_policy": current_settings.get("veto_policy", ""),
            "bandit_policy_json": current_settings.get("bandit_policy_json", ""),
            "map_stats": current_settings.get("map_stats", ""),
        },
        "team_explanations": team_explanations(snapshot_rows, current),
    }


def load_prediction(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def csv_columns(path: str | Path) -> set[str]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return set(csv.DictReader(handle).fieldnames or [])


def combine_history(rows: list[dict[str, float]]) -> dict[str, float]:
    total = sum(row["team_count"] for row in rows) or 1.0
    output = {"team_count": total}
    for key in ("brier_score", "log_loss", "advance_accuracy"):
        output[key] = sum(row[key] * row["team_count"] for row in rows) / total
    return output


def uncertainty_rows(prediction: dict[str, object]) -> list[dict[str, object]]:
    card = prediction["pickem_card"]  # type: ignore[index]
    rows_by_team = {row["team"]: row for row in prediction["probabilities"]}  # type: ignore[index]
    output: list[dict[str, object]] = []
    for slot, teams in (
        ("3-0", card["three_zero"]),
        ("晋级(3-1/3-2)", card["advance"]),
        ("0-3", card["zero_three"]),
    ):
        for team in teams:
            row = rows_by_team[team]
            if slot == "3-0":
                probability = parse_percent(row["p_3_0"])
            elif slot == "0-3":
                probability = parse_percent(row["p_0_3"])
            else:
                probability = parse_percent(row.get("p_pickem_advance", "0%"))
            output.append({"team": team, "slot": slot, "slot_probability": probability, "tier": uncertainty_tier(slot, probability)})
    return output


def uncertainty_tier(slot: str, probability: float) -> str:
    if slot == "晋级(3-1/3-2)":
        if probability >= 0.55:
            return "稳选"
        if probability >= 0.42:
            return "边缘"
        return "高风险"
    if probability >= 0.25:
        return "稳选"
    if probability >= 0.14:
        return "边缘"
    return "高风险"


def team_explanations(snapshot_rows: list[dict[str, str]], prediction: dict[str, object]) -> list[dict[str, object]]:
    probabilities = {row["team"]: row for row in prediction["probabilities"]}  # type: ignore[index]
    stats = feature_stats(snapshot_rows)
    output: list[dict[str, object]] = []
    for row in snapshot_rows:
        team = row["team"]
        plus: list[tuple[float, str]] = []
        minus: list[tuple[float, str]] = []
        for feature, label in POSITIVE_SIGNALS.items():
            score = z_score(row, feature, stats)
            if score >= 0:
                plus.append((score, label))
            else:
                minus.append((-score, label + "偏低"))
        for feature, label in NEGATIVE_SIGNALS.items():
            score = z_score(row, feature, stats)
            if score <= 0:
                plus.append((-score, label + "较低"))
            else:
                minus.append((score, label))
        probability = probabilities.get(team, {})
        output.append(
            {
                "team": team,
                "p_advance": probability.get("p_advance", ""),
                "most_common_record": probability.get("most_common_record", ""),
                "positive": [label for _, label in sorted(plus, reverse=True)[:5]],
                "negative": [label for _, label in sorted(minus, reverse=True)[:5]],
            }
        )
    return output


def feature_stats(rows: list[dict[str, str]]) -> dict[str, tuple[float, float]]:
    output: dict[str, tuple[float, float]] = {}
    for feature in set(POSITIVE_SIGNALS) | set(NEGATIVE_SIGNALS):
        values = [float(row.get(feature, "") or 0.0) for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        output[feature] = (mean, variance ** 0.5 or 1.0)
    return output


def z_score(row: dict[str, str], feature: str, stats: dict[str, tuple[float, float]]) -> float:
    mean, std = stats[feature]
    return (float(row.get(feature, "") or 0.0) - mean) / std


def has_nonzero(rows: list[dict[str, str]], column: str) -> bool:
    values = []
    for row in rows:
        try:
            values.append(float(row.get(column, "") or 0.0))
        except ValueError:
            continue
    return bool(values) and any(abs(value) > 1e-9 for value in values)


def parse_percent(value: object) -> float:
    text = str(value).strip()
    if text.endswith("%"):
        return float(text[:-1]) / 100.0
    return float(text)


def render_report(payload: dict[str, object]) -> str:
    current = payload["current"]  # type: ignore[assignment]
    overfit = payload["overfit_evaluation"]  # type: ignore[assignment]
    constraints = payload["direction_constraints"]  # type: ignore[assignment]
    temporal = payload["temporal_vrs"]  # type: ignore[assignment]
    calibration = payload["bo1_bo3_calibration"]  # type: ignore[assignment]
    veto_counter = payload["veto_counter_simulation"]  # type: ignore[assignment]
    lines = [
        f"# {payload['model']} 合理性报告",
        "",
        "## 当前 Cologne Pick'Em",
        "",
        f"- 通过率: `{current['pass_probability']:.1%}`",
        f"- 期望猜中: `{current['expected_correct']:.2f}`",
        f"- Pick'Em 卡: 3-0 {', '.join(current['pickem_card']['three_zero'])}; 晋级(3-1/3-2) {', '.join(current['pickem_card']['advance'])}; 0-3 {', '.join(current['pickem_card']['zero_three'])}",
        "",
        "## 反过拟合评估",
        "",
        "| 赛事 | Pick'Em通过率 | 期望猜中 | Brier | 对数损失 | 晋级命中率 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, name in (("austin", "Austin 2025 Stage 1"), ("budapest", "Budapest 2025 Stage 1"), ("combined", "合并")):
        row = overfit[key]
        pass_probability = row.get("pass_probability")
        expected_correct = row.get("expected_correct")
        lines.append(
            "| {name} | {pass_probability} | {expected_correct} | {brier:.4f} | {logloss:.4f} | {accuracy:.1%} |".format(
                name=name,
                pass_probability=f"{pass_probability:.1%}" if pass_probability is not None else "n/a",
                expected_correct=f"{expected_correct:.2f}" if expected_correct is not None else "n/a",
                brier=row["brier_score"],
                logloss=row["log_loss"],
                accuracy=row["advance_accuracy"],
            )
        )
    lines.extend(
        [
            "",
            "## 合理性护栏",
            "",
            f"- 方向约束启用: `{constraints['enabled']}`",
            f"- BO1/BO3 校准: scale={calibration.get('scale')}, bo1_shrink={calibration.get('bo1_shrink')}, bo3_shrink={calibration.get('bo3_shrink')}, veto_weight={calibration.get('veto_weight')}",
            f"- 对阵级 veto 反制模拟: `{veto_counter['enabled']}`，策略 `{veto_counter['veto_policy']}`",
            f"- VRS 时间快照数: `{len(temporal['vrs_files'])}`",
            f"- 预期分差残差进入快照: `{temporal['snapshot_has_expected_residual']}`",
            f"- 预期分差残差进入训练差值列: `{temporal['pretrain_has_expected_residual_diff']}`",
            "",
            "## 不确定性分层",
            "",
            "| 槽位 | 队伍 | 槽位概率 | 分层 |",
            "|---|---|---:|---|",
        ]
    )
    for row in current["uncertainty"]:
        lines.append(f"| {row['slot']} | {row['team']} | {row['slot_probability']:.1%} | {row['tier']} |")
    lines.extend(["", "## 队伍解释卡", "", "| 队伍 | 晋级 | 常见战绩 | 加分项 | 扣分项 |", "|---|---:|---|---|---|"])
    for row in payload["team_explanations"]:  # type: ignore[index]
        lines.append(
            "| {team} | {p_advance} | {most_common_record} | {positive} | {negative} |".format(
                team=row["team"],
                p_advance=row["p_advance"],
                most_common_record=row["most_common_record"],
                positive="；".join(row["positive"]),
                negative="；".join(row["negative"]),
            )
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
