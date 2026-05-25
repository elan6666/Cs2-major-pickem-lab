from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import PickemCard, TeamProbability


def probability_rows(probabilities: list[TeamProbability]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in probabilities:
        probs = item.record_probabilities
        rows.append(
            {
                "team": item.team.name,
                "seed": str(item.team.seed),
                "score": f"{item.team.score:.1f}",
                "p_3_0": format_probability(probs["3-0"]),
                "p_3_1": format_probability(probs["3-1"]),
                "p_3_2": format_probability(probs["3-2"]),
                "p_pickem_advance": format_probability(item.pickem_advance_probability),
                "p_advance": format_probability(item.advance_probability),
                "p_2_3": format_probability(probs["2-3"]),
                "p_1_3": format_probability(probs["1-3"]),
                "p_0_3": format_probability(probs["0-3"]),
                "most_common_record": item.most_common_record,
            }
        )
    return rows


def format_probability(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_probability_csv(path: str | Path, probabilities: list[TeamProbability]) -> None:
    rows = probability_rows(probabilities)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json_summary(
    path: str | Path,
    probabilities: list[TeamProbability],
    card: PickemCard,
    settings: dict[str, object],
) -> None:
    payload = {
        "settings": settings,
        "probabilities": probability_rows(probabilities),
        "pickem_card": {
            "three_zero": card.three_zero,
            "zero_three": card.zero_three,
            "advance": card.advance,
            "pass_probability": card.pass_probability,
            "expected_correct": card.expected_correct,
        },
    }
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def render_markdown_report(
    probabilities: list[TeamProbability],
    card: PickemCard,
    settings: dict[str, object],
) -> str:
    stage_name = str(settings.get("stage_name") or "Stage 1")
    advance_label = str(settings.get("advance_label") or "Advance")
    lines = [
        f"# CS2 Major {stage_name} 预测报告",
        "",
        "## 运行设置",
        "",
    ]
    for key, value in settings.items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## 推荐 Pick'Em 卡",
            "",
            f"- 3-0: {', '.join(card.three_zero)}",
            f"- 0-3: {', '.join(card.zero_three)}",
            f"- {advance_label}: {', '.join(card.advance)}",
            f"- 预计通过概率: {format_probability(card.pass_probability)}",
            f"- 期望猜中数: {card.expected_correct:.2f}",
            "",
            "## 队伍概率",
            "",
            f"| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | {advance_label} | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )

    for row in probability_rows(probabilities):
        lines.append(
            "| {team} | {seed} | {score} | {p_3_0} | {p_3_1} | {p_3_2} | {p_pickem_advance} | {p_advance} | {p_2_3} | {p_1_3} | {p_0_3} | {most_common_record} |".format(
                **row
            )
        )

    lines.extend(["", "## 注意事项", ""])
    lines.append(
        "- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。"
    )
    lines.append("- 赔率不作为模型输入。")
    if settings.get("feature_snapshot"):
        lines.append("- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。")
    else:
        lines.append("- 本次运行没有使用 HLTV 特征输入。")
    if settings.get("map_stats"):
        lines.append("- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。")
    else:
        lines.append("- 本次运行没有启用地图 veto 模拟。")
    lines.append("- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。")
    lines.append("- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。")
    return "\n".join(lines) + "\n"


def write_markdown_report(path: str | Path, content: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
