from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .catboost_model import PairwiseExample, build_pairwise_examples, load_pretrain_examples, train_catboost_model
from .data_provenance import is_bo3_url, validate_pretrain_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train Stage 1 CatBoost pairwise model")
    parser.add_argument("--pretrain-matches", help="Optional last-4-month 16-team vs VRS Top 100 match/map CSV")
    parser.add_argument("--require-real-pretrain", action="store_true", help="Fail unless --pretrain-matches has accepted real-source provenance")
    parser.add_argument("--snapshots", nargs="+", required=True, help="Major Stage 1 pre-event snapshots")
    parser.add_argument("--labels", nargs="+", required=True, help="Major Stage 1 outcome labels")
    parser.add_argument("--model-output", required=True, help="CatBoost binary model output")
    parser.add_argument("--metadata-json", required=True, help="Model metadata JSON")
    parser.add_argument("--report", required=True, help="Markdown report output")
    parser.add_argument("--iterations", type=int, default=120)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--l2-leaf-reg", type=float, default=8.0)
    parser.add_argument("--pretrain-weight-scale", type=float, default=1.0)
    parser.add_argument("--major-weight-scale", type=float, default=1.0)
    parser.add_argument("--training-mode-name", default="")
    parser.add_argument("--use-directional-constraints", action="store_true", help="Constrain directional numeric features to match domain priors")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    major_examples = scale_examples(build_pairwise_examples(args.snapshots, args.labels), args.major_weight_scale)
    examples = list(major_examples)
    pretrain_count = 0
    pretrain_mode = "fallback_major_pairwise"
    if args.pretrain_matches:
        pretrain_path = Path(args.pretrain_matches)
        if pretrain_path.exists():
            provenance = validate_pretrain_csv(pretrain_path)
            if not provenance.ok:
                raise ValueError(
                    "Pretrain match/map CSV failed real-data provenance validation: "
                    + "; ".join(provenance.errors)
                )
            pretrain_examples = scale_examples(load_pretrain_examples(pretrain_path), args.pretrain_weight_scale)
            pretrain_count = len(pretrain_examples)
            pretrain_mode = infer_pretrain_mode(pretrain_path)
            examples = pretrain_examples + examples
        else:
            raise ValueError(f"Pretrain match/map CSV does not exist: {args.pretrain_matches}")
    elif args.require_real_pretrain:
        raise ValueError("--require-real-pretrain requires --pretrain-matches with real HLTV provenance")

    metadata = train_catboost_model(
        examples=examples,
        model_path=args.model_output,
        iterations=args.iterations,
        depth=args.depth,
        learning_rate=args.learning_rate,
        l2_leaf_reg=args.l2_leaf_reg,
        use_directional_constraints=args.use_directional_constraints,
    )
    metadata.update(
        {
            "stage1_training_mode": pretrain_mode,
            "stage1_pretrain_match_map_rows": pretrain_count,
            "stage2_training_mode": args.training_mode_name or "austin_budapest_major_calibration_weighted_pairwise",
            "stage2_major_pairwise_rows": len(major_examples),
            "pretrain_weight_scale": args.pretrain_weight_scale,
            "major_weight_scale": args.major_weight_scale,
            "snapshots": args.snapshots,
            "labels": args.labels,
            "warning": (
                "No last-4-month featureized HLTV match/map pretraining rows were supplied; "
                "this model is runnable but should remain experimental until real pretraining data is added."
                if pretrain_count == 0
                else ""
            ),
        }
    )
    Path(args.metadata_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.metadata_json).write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(metadata), encoding="utf-8")
    print(f"Wrote CatBoost model to {args.model_output}")
    print(f"Wrote CatBoost metadata to {args.metadata_json}")
    return 0


def scale_examples(examples: list[PairwiseExample], factor: float) -> list[PairwiseExample]:
    if factor <= 0:
        raise ValueError("weight scale must be greater than 0")
    return [replace(example, weight=example.weight * factor) for example in examples]


def render_report(metadata: dict[str, object]) -> str:
    lines = [
        "# Stage 1 CatBoost 训练报告",
        "",
        "## 两阶段训练状态",
        "",
        f"- 第一阶段：近 4 个月 16 支队伍 vs VRS Top 100 match/map 预训练行数：{metadata['stage1_pretrain_match_map_rows']}",
        f"- 第一阶段模式：`{metadata['stage1_training_mode']}`",
        f"- 第二阶段：`{metadata['stage2_training_mode']}`",
        f"- 第二阶段 Major pairwise 行数：{metadata.get('stage2_major_pairwise_rows', 0)}",
        f"- 近 4 个月 BO3 权重倍率：{metadata.get('pretrain_weight_scale', 1.0)}",
        f"- Major 校准权重倍率：{metadata.get('major_weight_scale', 1.0)}",
        f"- 训练样本：{metadata['example_count']} pairwise examples",
        "",
        "## 模型参数",
        "",
        f"- iterations: {metadata['params']['iterations']}",  # type: ignore[index]
        f"- depth: {metadata['params']['depth']}",  # type: ignore[index]
        f"- learning_rate: {metadata['params']['learning_rate']}",  # type: ignore[index]
        f"- l2_leaf_reg: {metadata['params']['l2_leaf_reg']}",  # type: ignore[index]
        "",
        "## 说明",
        "",
        "这个模型已经能完整进入 Stage 1 瑞士轮 + Pick'Em 预测链路。若没有真实近 4 个月 match/map 预训练表，它会退化为 Austin/Budapest Stage 1 最终标签的弱监督两两对比训练，不能当作稳定生产模型。",
    ]
    warning = str(metadata.get("warning", ""))
    if warning:
        lines.extend(["", "## 风险", "", warning])
    return "\n".join(lines) + "\n"


def infer_pretrain_mode(path: Path) -> str:
    import csv

    with path.open(newline="", encoding="utf-8") as handle:
        sources = [row.get("source_url", "") for row in csv.DictReader(handle)]
    if any(is_bo3_url(source) for source in sources):
        return "last_4_month_bo3_pretrain"
    return "last_4_month_hltv_pretrain"


if __name__ == "__main__":
    raise SystemExit(main())
