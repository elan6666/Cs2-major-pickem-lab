from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
from pathlib import Path


RADAR_DIMENSIONS = [
    ("base_strength_factor", "基础实力"),
    ("hltv_rating_factor", "HLTV状态"),
    ("firepower_factor", "火力"),
    ("map_pool_depth_factor", "地图样本"),
    ("sample_confidence_factor", "样本置信"),
    ("opponent_quality_proxy_factor", "对手池"),
    ("roster_data_factor", "阵容数据"),
    ("seed_path_factor", "种子路径"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从 Stage 1 因素快照生成中文雷达图")
    parser.add_argument("--snapshot", required=True, help="因素综合快照 CSV")
    parser.add_argument("--output", required=True, help="输出 SVG")
    parser.add_argument("--columns", type=int, default=4, help="小多图网格列数")
    parser.add_argument("--team-png-dir", help="可选：为每支队伍输出一张 PNG 雷达图的目录")
    parser.add_argument("--prediction-json", help="可选：主模型预测 JSON，用于在单队 PNG 中标注预测概率")
    parser.add_argument("--model-name", default="weighted-finetune-latest", help="单队 PNG 标注的模型名称")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_rows(args.snapshot)
    svg = render_radar_grid(rows, columns=args.columns)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    print(f"Wrote radar SVG to {args.output}")
    if args.team_png_dir:
        predictions = load_predictions(args.prediction_json) if args.prediction_json else {}
        written = render_team_pngs(rows, args.team_png_dir, predictions, args.model_name)
        print(f"Wrote {written} team radar PNG files to {args.team_png_dir}")
    return 0


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_predictions(path: str | Path) -> dict[str, dict[str, str]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {row["team"]: row for row in payload.get("probabilities", [])}


def render_radar_grid(rows: list[dict[str, str]], columns: int = 4) -> str:
    if not rows:
        raise ValueError("No rows to chart")
    columns = max(1, columns)
    ranked = sorted(rows, key=lambda row: float(row.get("factor_score", "0") or 0), reverse=True)
    cell_width = 270
    cell_height = 280
    title_height = 70
    rows_count = math.ceil(len(ranked) / columns)
    width = columns * cell_width
    height = title_height + rows_count * cell_height
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,'PingFang SC','Microsoft YaHei',sans-serif;fill:#1f2933} .muted{fill:#6b7280} .grid{stroke:#d9dee7;stroke-width:1;fill:none} .axis{stroke:#c6ccd6;stroke-width:1} .shape{fill:#2a9d8f;fill-opacity:.28;stroke:#1b7f74;stroke-width:2} .score{font-weight:700}",
        "</style>",
        '<rect width="100%" height="100%" fill="#fbfcfe"/>',
        '<text x="24" y="30" font-size="22" font-weight="700">IEM Cologne Major 2026 Stage 1 因素雷达图</text>',
        '<text x="24" y="54" font-size="13" class="muted">维度来自 VRS + 真实 HLTV 派生因素快照；暂缺的 veto、经济局、角色与韧性数据已在中文模型报告中说明。</text>',
    ]
    for index, row in enumerate(ranked):
        grid_x = index % columns
        grid_y = index // columns
        x = grid_x * cell_width
        y = title_height + grid_y * cell_height
        parts.append(render_team_radar(row, x, y, cell_width, cell_height))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_team_radar(row: dict[str, str], x: int, y: int, width: int, height: int) -> str:
    cx = width / 2
    cy = 150
    radius = 72
    values = [bounded_float(row.get(field, "0")) for field, _ in RADAR_DIMENSIONS]
    polygon = points_for_values(cx, cy, radius, values)
    rings = []
    for fraction in (0.25, 0.5, 0.75, 1.0):
        ring_values = [fraction * 100.0 for _ in RADAR_DIMENSIONS]
        rings.append(f'<polygon class="grid" points="{points_for_values(cx, cy, radius, ring_values)}"/>')
    axes = []
    labels = []
    for index, (_, label) in enumerate(RADAR_DIMENSIONS):
        angle = -math.pi / 2 + index * 2 * math.pi / len(RADAR_DIMENSIONS)
        x2 = cx + math.cos(angle) * radius
        y2 = cy + math.sin(angle) * radius
        lx = cx + math.cos(angle) * (radius + 19)
        ly = cy + math.sin(angle) * (radius + 19)
        anchor = "middle"
        if lx < cx - 10:
            anchor = "end"
        elif lx > cx + 10:
            anchor = "start"
        axes.append(f'<line class="axis" x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" dominant-baseline="middle" font-size="9" class="muted">{html.escape(label)}</text>'
        )
    team = html.escape(row.get("team", ""))
    score = html.escape(row.get("factor_score", ""))
    overall = html.escape(row.get("overall_factor_rating", ""))
    return "\n".join(
        [
            f'<g transform="translate({x},{y})">',
            f'<text x="16" y="24" font-size="15" font-weight="700">{team}</text>',
            f'<text x="16" y="43" font-size="12" class="muted">因素分 {score} | 综合 {overall}</text>',
            *rings,
            *axes,
            f'<polygon class="shape" points="{polygon}"/>',
            *labels,
            "</g>",
        ]
    )


def render_team_pngs(
    rows: list[dict[str, str]],
    output_dir: str | Path,
    predictions: dict[str, dict[str, str]],
    model_name: str,
) -> int:
    try:
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
    except ImportError as exc:  # pragma: no cover - exercised only when optional plotting dependency is absent.
        raise SystemExit("生成 PNG 需要 matplotlib。请先安装 matplotlib。") from exc

    font = find_chinese_font(font_manager)
    if font:
        plt.rcParams["font.family"] = font
    plt.rcParams["axes.unicode_minus"] = False

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    ranked = sorted(rows, key=lambda row: float(row.get("factor_score", "0") or 0), reverse=True)
    labels = [label for _, label in RADAR_DIMENSIONS]
    angles = [index * 2 * math.pi / len(labels) for index in range(len(labels))]
    closed_angles = angles + angles[:1]

    for rank, row in enumerate(ranked, start=1):
        values = [bounded_float(row.get(field, "0")) for field, _ in RADAR_DIMENSIONS]
        closed_values = values + values[:1]
        team = row.get("team", "")
        prediction = predictions.get(team, {})
        fig = plt.figure(figsize=(6.0, 6.4), dpi=180)
        ax = fig.add_subplot(111, polar=True)
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)
        ax.plot(closed_angles, closed_values, color="#1b7f74", linewidth=2.2)
        ax.fill(closed_angles, closed_values, color="#2a9d8f", alpha=0.26)
        ax.scatter(angles, values, s=24, color="#1b7f74", zorder=3)
        ax.set_xticks(angles)
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(["25", "50", "75", "100"], fontsize=8, color="#6b7280")
        ax.grid(color="#d9dee7", linewidth=0.8)
        ax.spines["polar"].set_color("#c6ccd6")

        subtitle = [
            f"因素分 {row.get('factor_score', '')} | 综合 {row.get('overall_factor_rating', '')}",
            f"主模型 {model_name}",
        ]
        if prediction:
            subtitle.append(
                "晋级 {advance} | 3-0 {three_zero} | 0-3 {zero_three} | 常见 {record}".format(
                    advance=prediction.get("p_advance", ""),
                    three_zero=prediction.get("p_3_0", ""),
                    zero_three=prediction.get("p_0_3", ""),
                    record=prediction.get("most_common_record", ""),
                )
            )
        fig.suptitle(f"{rank}. {team}", fontsize=18, fontweight="bold", y=0.98, color="#1f2933")
        fig.text(0.5, 0.905, "\n".join(subtitle), ha="center", va="top", fontsize=10, color="#4b5563")
        fig.text(0.5, 0.035, "维度：VRS、HLTV、火力、地图样本、样本置信、对手池、阵容数据、种子路径", ha="center", fontsize=8.5, color="#6b7280")
        fig.tight_layout(rect=(0.04, 0.06, 0.96, 0.86))
        fig.savefig(output / f"{slugify(team)}_radar.png", bbox_inches="tight", facecolor="#fbfcfe")
        plt.close(fig)
    return len(ranked)


def find_chinese_font(font_manager) -> str | None:
    preferred = (
        "PingFang SC",
        "Hiragino Sans GB",
        "Microsoft YaHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "SimHei",
    )
    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            return name
    return None


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "team"


def points_for_values(cx: float, cy: float, radius: float, values: list[float]) -> str:
    points = []
    for index, value in enumerate(values):
        angle = -math.pi / 2 + index * 2 * math.pi / len(values)
        scaled = radius * max(0.0, min(100.0, value)) / 100.0
        points.append(f"{cx + math.cos(angle) * scaled:.1f},{cy + math.sin(angle) * scaled:.1f}")
    return " ".join(points)


def bounded_float(value: str | None) -> float:
    if value is None or value == "":
        return 0.0
    return max(0.0, min(100.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
