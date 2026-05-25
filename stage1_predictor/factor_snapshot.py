from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


FACTOR_WEIGHTS = {
    "base_strength_factor": 0.35,
    "hltv_rating_factor": 0.15,
    "firepower_factor": 0.10,
    "map_pool_depth_factor": 0.08,
    "sample_confidence_factor": 0.08,
    "opponent_quality_proxy_factor": 0.12,
    "roster_data_factor": 0.05,
    "seed_path_factor": 0.07,
}

UNAVAILABLE_FACTORS = (
    "地图 veto 与 ban/pick 倾向",
    "单地图近期胜率与按对手排名分层的地图胜率",
    "T/CT 阵营强度拆分",
    "手枪局、force-buy、eco、anti-eco 等经济局数据",
    "选手角色指标，例如 entry、AWP、KAST、ADR、impact、clutch",
    "战术风格与克制标签",
    "韧性状态，例如 0-5 落后、加时、图三、淘汰局、晋级局表现",
    "同阵容、同地图池条件下的近期交手",
    "赛程压力、旅行、健康、签证与替补信号",
)

REGION_OPPONENT_POOL_FACTORS = {
    "EU": 100.0,
    "Europe": 100.0,
    "Americas": 75.0,
    "Asia": 65.0,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a factor-score snapshot from a Stage 1 HLTV feature snapshot")
    parser.add_argument("--input", required=True, help="Input HLTV feature snapshot CSV")
    parser.add_argument("--output", required=True, help="Output factor snapshot CSV")
    parser.add_argument("--weights-json", help="Optional trained factor weights JSON")
    parser.add_argument("--report", help="Optional Markdown report describing the factor formula")
    parser.add_argument("--json", help="Optional JSON formula metadata output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_rows(args.input)
    weights = load_factor_weights(args.weights_json) if args.weights_json else FACTOR_WEIGHTS
    factor_rows = build_factor_rows(rows, weights)
    write_rows(args.output, factor_rows)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(render_factor_report(args.input, args.output, factor_rows, weights), encoding="utf-8")
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps(
                {
                    "input": args.input,
                    "output": args.output,
                    "weights": weights,
                    "unavailable_factors": UNAVAILABLE_FACTORS,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"Wrote factor snapshot to {args.output}")
    return 0


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_factor_weights(path: str | Path) -> dict[str, float]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    weights = payload.get("weights", payload.get("trained_weights", payload))
    return normalize_factor_weights({name: float(weights[name]) for name in FACTOR_WEIGHTS})


def normalize_factor_weights(weights: dict[str, float]) -> dict[str, float]:
    missing = sorted(set(FACTOR_WEIGHTS) - set(weights))
    extra = sorted(set(weights) - set(FACTOR_WEIGHTS))
    if missing:
        raise ValueError(f"Missing factor weights: {', '.join(missing)}")
    if extra:
        raise ValueError(f"Unknown factor weights: {', '.join(extra)}")
    if any(value < 0 for value in weights.values()):
        raise ValueError("Factor weights must be non-negative")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Factor weights must sum to a positive value")
    return {name: weights[name] / total for name in FACTOR_WEIGHTS}


def write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No factor rows to write")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_factor_rows(rows: list[dict[str, str]], weights: dict[str, float] | None = None) -> list[dict[str, str]]:
    if not rows:
        raise ValueError("Input snapshot has no rows")
    active_weights = normalize_factor_weights(weights or FACTOR_WEIGHTS)

    vrs_values = [number(row, "vrs_points", number(row, "score", 0.0)) for row in rows]
    seed_values = [17.0 - number(row, "seed", 16.0) for row in rows]
    rating_values = [number(row, "hltv_rating3", 1.0) for row in rows]
    kd_values = [optional_number(row, "hltv_kd") for row in rows]
    kd_per_map_values = [kd_diff_per_map(row) for row in rows]
    map_depth_values = [math.log1p(number(row, "hltv_maps", 0.0)) for row in rows]
    sample_values = [min(100.0, number(row, "hltv_maps", 0.0) / 300.0 * 100.0) for row in rows]

    normalized_kd = normalize_optional(kd_values)
    normalized_kd_per_map = normalize_optional(kd_per_map_values)

    output: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        base_strength = normalize(vrs_values[index], vrs_values)
        seed_path = normalize(seed_values[index], seed_values)
        hltv_rating = normalize(rating_values[index], rating_values)
        map_pool_depth = normalize(map_depth_values[index], map_depth_values)
        sample_confidence = sample_values[index]
        opponent_quality = REGION_OPPONENT_POOL_FACTORS.get(row.get("region", "").strip(), 70.0)
        roster_data = roster_data_factor(row)
        firepower = mean_available(
            [
                hltv_rating,
                normalized_kd[index],
                normalized_kd_per_map[index],
            ]
        )
        factors = {
            "base_strength_factor": base_strength,
            "seed_path_factor": seed_path,
            "hltv_rating_factor": hltv_rating,
            "firepower_factor": firepower,
            "map_pool_depth_factor": map_pool_depth,
            "sample_confidence_factor": sample_confidence,
            "opponent_quality_proxy_factor": opponent_quality,
            "roster_data_factor": roster_data,
        }
        overall = sum(factors[name] * weight for name, weight in active_weights.items())
        factor_score = 1250.0 + overall * 4.2
        enriched = dict(row)
        enriched.update({name: f"{value:.2f}" for name, value in factors.items()})
        enriched["overall_factor_rating"] = f"{overall:.2f}"
        enriched["factor_score"] = f"{factor_score:.2f}"
        enriched["included_factor_notes"] = included_factor_notes(row)
        enriched["unavailable_factor_notes"] = "; ".join(UNAVAILABLE_FACTORS)
        output.append(enriched)

    return output


def normalize(value: float, values: list[float]) -> float:
    low = min(values)
    high = max(values)
    if high == low:
        return 50.0
    return (value - low) / (high - low) * 100.0


def normalize_optional(values: list[float | None]) -> list[float | None]:
    present = [value for value in values if value is not None]
    if not present:
        return [None for _ in values]
    return [None if value is None else normalize(value, present) for value in values]


def mean_available(values: list[float | None]) -> float:
    present = [value for value in values if value is not None]
    if not present:
        return 50.0
    return sum(present) / len(present)


def number(row: dict[str, str], field: str, default: float) -> float:
    value = row.get(field, "").strip()
    if not value:
        return default
    return float(value)


def optional_number(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "").strip()
    if not value:
        return None
    return float(value)


def kd_diff_per_map(row: dict[str, str]) -> float | None:
    kd_diff = optional_number(row, "hltv_kd_diff")
    maps = number(row, "hltv_maps", 0.0)
    if kd_diff is None or maps <= 0:
        return None
    return kd_diff / maps


def roster_data_factor(row: dict[str, str]) -> float:
    maps = number(row, "hltv_maps", 0.0)
    source_type = row.get("hltv_source_type", "")
    if source_type == "team_overview_current_roster":
        return min(100.0, maps / 150.0 * 100.0)
    if source_type == "team_stats_all_time":
        return 65.0
    return min(50.0, maps / 150.0 * 100.0)


def included_factor_notes(row: dict[str, str]) -> str:
    return "; ".join(
        [
            "比赛语境：Stage 1 瑞士轮、BO1/BO3 收缩、晋级局/淘汰局 BO3 由模拟器处理",
            "基础实力：VRS 积分与种子路径",
            "近期状态/火力：HLTV Rating 3.0、K/D、每图 K-D 差，缺失时回退到 rating",
            "地图池代理：HLTV 地图样本量；暂不等同于真实强图或 veto 优势",
            f"对手池代理：赛区={row.get('region', '')}",
            f"阵容数据置信度：来源={row.get('hltv_source_type', '')}",
        ]
    )


def render_factor_report(
    input_path: str,
    output_path: str,
    rows: list[dict[str, str]],
    weights: dict[str, float] | None = None,
) -> str:
    active_weights = normalize_factor_weights(weights or FACTOR_WEIGHTS)
    ranked = sorted(rows, key=lambda row: float(row["factor_score"]), reverse=True)
    lines = [
        "# Stage 1 因素综合模型",
        "",
        "这是科隆 Major 2026 Stage 1 的可解释评分层。它优先选取目前能从本地 VRS 与真实 HLTV 派生快照中稳定获得、且对胜负判断有实际价值的因素，生成 `factor_score` 后交给现有瑞士轮蒙特卡洛模拟器。",
        "",
        f"- 输入快照：`{input_path}`",
        f"- 输出快照：`{output_path}`",
        "",
        "## 已纳入因素",
        "",
        "| 因素 | 权重 | 数据来源 | 说明 |",
        "|---|---:|---|---|",
        f"| 基础实力 | {active_weights['base_strength_factor']:.0%} | Valve Regional Standings 积分 | 作为赛前稳定强度锚点，避免只看近期小样本。 |",
        f"| HLTV Rating | {active_weights['hltv_rating_factor']:.0%} | HLTV Rating 3.0 | 作为近期状态/团队表现代理，但不能替代对手质量修正。 |",
        f"| 火力代理 | {active_weights['firepower_factor']:.0%} | HLTV Rating 3.0、K/D、每图 K-D 差 | 尽量使用团队火力指标；K/D 缺失时回退到 rating。 |",
        f"| 地图池深度代理 | {active_weights['map_pool_depth_factor']:.0%} | HLTV 地图样本量 | 这里只衡量样本深度，还不是真实强图、弱图或 veto 优势。 |",
        f"| 样本置信度 | {active_weights['sample_confidence_factor']:.0%} | HLTV 地图样本量 | 对样本很薄的队伍做保守处理。 |",
        f"| 对手池代理 | {active_weights['opponent_quality_proxy_factor']:.0%} | 赛区先验 | 在没有 Top 5/10/20 分层对手数据前，先做跨赛区修正。 |",
        f"| 阵容数据置信度 | {active_weights['roster_data_factor']:.0%} | HLTV 来源类型与地图数 | 区分全队历史统计与当前阵容页代理。 |",
        f"| 种子路径 | {active_weights['seed_path_factor']:.0%} | Stage 1 种子 | 体现已知开局路径，但权重较低，避免重复计算 VRS。 |",
        "",
        "## 模型排名",
        "",
        "| 排名 | 队伍 | 因素分 | 综合百分位 | VRS | HLTV Rating | 火力 | 地图深度 | 样本 | 对手池 | 阵容数据 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(ranked, start=1):
        lines.append(
            "| {rank} | {team} | {factor_score} | {overall_factor_rating} | {base_strength_factor} | {hltv_rating_factor} | {firepower_factor} | {map_pool_depth_factor} | {sample_confidence_factor} | {opponent_quality_proxy_factor} | {roster_data_factor} |".format(
                rank=rank,
                **row,
            )
        )
    lines.extend(["", "## 暂未纳入因素", ""])
    lines.extend(f"- {factor}" for factor in UNAVAILABLE_FACTORS)
    lines.extend(
        [
            "",
            "策略：这版模型先作为实验模型保留。只有当它在已完成 Stage 1 的回测、校准和 Pick'Em 通过率上持续优于 VRS-only 时，才应该提升为默认模型；不能因为因素更多就默认更准。",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
