from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_probability(value: str) -> float:
    return float(value.rstrip("%")) / 100


def load_summary(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_comparison(baseline_path: str | Path, candidate_path: str | Path) -> str:
    baseline = load_summary(baseline_path)
    candidate = load_summary(candidate_path)
    baseline_rows = {row["team"]: row for row in baseline["probabilities"]}  # type: ignore[index]
    candidate_rows = {row["team"]: row for row in candidate["probabilities"]}  # type: ignore[index]

    lines = [
        "# Stage 1 预测模型对比",
        "",
        f"- 基线: `{baseline_path}`",
        f"- 候选: `{candidate_path}`",
        "",
        "## Pick'Em Card",
        "",
        "| 模型 | 3-0 | 0-3 | 晋级 | 通过概率 | 期望猜中 |",
        "|---|---|---|---|---:|---:|",
    ]
    for label, payload in (("基线", baseline), ("候选", candidate)):
        card = payload["pickem_card"]  # type: ignore[index]
        lines.append(
            "| {label} | {three_zero} | {zero_three} | {advance} | {pass_probability:.1%} | {expected_correct:.2f} |".format(
                label=label,
                three_zero=", ".join(card["three_zero"]),
                zero_three=", ".join(card["zero_three"]),
                advance=", ".join(card["advance"]),
                pass_probability=float(card["pass_probability"]),
                expected_correct=float(card["expected_correct"]),
            )
        )

    changes = []
    for team, baseline_row in baseline_rows.items():
        candidate_row = candidate_rows[team]
        changes.append(
            {
                "team": team,
                "advance_delta": parse_probability(candidate_row["p_advance"]) - parse_probability(baseline_row["p_advance"]),
                "three_zero_delta": parse_probability(candidate_row["p_3_0"]) - parse_probability(baseline_row["p_3_0"]),
                "zero_three_delta": parse_probability(candidate_row["p_0_3"]) - parse_probability(baseline_row["p_0_3"]),
            }
        )

    lines.extend(
        [
            "",
            "## 晋级概率变化最大的队伍",
            "",
            "| 队伍 | 晋级变化 | 3-0 变化 | 0-3 变化 |",
            "|---|---:|---:|---:|",
        ]
    )
    for item in sorted(changes, key=lambda row: abs(row["advance_delta"]), reverse=True)[:8]:
        lines.append(
            f"| {item['team']} | {item['advance_delta']:+.1%} | {item['three_zero_delta']:+.1%} | {item['zero_three_delta']:+.1%} |"
        )

    lines.extend(
        [
            "",
            "## 解读",
            "",
            "候选模型仍是实验模型。除非它在回测和人工复核中给出更可信的概率，否则默认仍应保留基线模型。",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare two Stage 1 prediction JSON summaries")
    parser.add_argument("--baseline-json", required=True)
    parser.add_argument("--candidate-json", required=True)
    parser.add_argument("--report", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = render_comparison(args.baseline_json, args.candidate_json)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")
    print(f"Wrote comparison report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
