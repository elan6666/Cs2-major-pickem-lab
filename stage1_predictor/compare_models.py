from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_summary(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_summary_arg(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected NAME=path")
    name, path = value.split("=", 1)
    if not name or not path:
        raise argparse.ArgumentTypeError("Expected NAME=path")
    return name, path


def model_rows(summaries: list[tuple[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, path in summaries:
        payload = load_summary(path)
        card = payload["pickem_card"]  # type: ignore[index]
        settings = payload.get("settings", {})  # type: ignore[assignment]
        rows.append(
            {
                "model": name,
                "path": path,
                "configured_model": settings.get("model", "legacy"),  # type: ignore[union-attr]
                "three_zero": ", ".join(card["three_zero"]),
                "zero_three": ", ".join(card["zero_three"]),
                "advance": ", ".join(card["advance"]),
                "pass_probability": float(card["pass_probability"]),
                "expected_correct": float(card["expected_correct"]),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -float(row["pass_probability"]),
            -float(row["expected_correct"]),
            0 if str(row["model"]) == "vrs" else 1,
            str(row["model"]),
        ),
    )


def render_report(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Stage 1 模型对比",
        "",
        "这份报告对比已生成的 Stage 1 预测输出。它是预测结果对比，不等同于已完成历史回测。",
        "",
        "## 排名",
        "",
        "| 排名 | 模型 | 配置模型 | 通过概率 | 期望猜中 | 3-0 | 0-3 | 晋级 |",
        "|---:|---|---|---:|---:|---|---|---|",
    ]
    for rank, row in enumerate(rows, start=1):
        lines.append(
            "| {rank} | {model} | {configured_model} | {pass_probability:.1%} | {expected_correct:.2f} | {three_zero} | {zero_three} | {advance} |".format(
                rank=rank,
                **row,
            )
        )
    lines.extend(
        [
            "",
            "## 策略",
            "",
            "默认保守模型仍保持纯 VRS。`factor-veto`/`factor-score` 是机制完整的规则版；CatBoost 系列使用近 4 个月 16 队 vs VRS Top 100 的 BO3 match/map 基础语料、BO3 地图禁选动作、Glicko 风格不确定性特征，以及 Austin/Budapest Stage 1 标签校准。所有 CatBoost 结果仍应视为实验预测，不等同于稳定历史回测结论。",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Stage 1 model output summaries")
    parser.add_argument("--summary", action="append", required=True, type=parse_summary_arg, help="Model summary in NAME=path form")
    parser.add_argument("--report", required=True, help="Output Markdown report path")
    parser.add_argument("--json", help="Optional JSON output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = model_rows(args.summary)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(rows), encoding="utf-8")
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps({"models": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote model comparison report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
