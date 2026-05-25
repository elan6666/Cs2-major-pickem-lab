from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bandit_veto import train_bandit_policy_from_csv, train_two_layer_bandit_policy_from_csv
from .map_veto import DEFAULT_MAP_POOL, load_map_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train or build a contextual bandit veto policy")
    parser.add_argument("--veto-actions", help="Optional true veto action CSV")
    parser.add_argument("--major-veto-actions", help="Optional Major true veto action CSV used as a correction layer")
    parser.add_argument("--major-correction-weight", type=float, default=0.50)
    parser.add_argument("--map-stats", help="Fallback map stats CSV for prior policy")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--report", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.veto_actions and args.major_veto_actions:
        payload = train_two_layer_bandit_policy_from_csv(
            args.veto_actions,
            args.major_veto_actions,
            args.output_json,
            major_correction_weight=args.major_correction_weight,
        )
        mode = "two_layer_recent_bo3_with_major_correction"
    elif args.veto_actions:
        payload = train_bandit_policy_from_csv(args.veto_actions, args.output_json)
        mode = "true_veto_action_bandit"
    elif args.map_stats:
        payload = build_prior_policy(args.map_stats)
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        mode = "map_stats_prior_bandit"
    else:
        payload = {"map_rewards": {name: 0.0 for name in DEFAULT_MAP_POOL}, "action_rewards": {}, "exploration": 0.20}
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        mode = "neutral_prior_bandit"
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(mode, payload), encoding="utf-8")
    print(f"Wrote bandit veto policy to {args.output_json}")
    return 0


def build_prior_policy(map_stats_path: str) -> dict[str, object]:
    stats = load_map_stats(map_stats_path)
    totals: dict[str, list[float]] = {}
    for team_maps in stats.values():
        for map_name, stat in team_maps.items():
            confidence = stat.confidence
            reward = ((stat.win_rate - 50.0) / 50.0) * confidence
            reward += (stat.pick_rate - stat.ban_rate) / 100.0 * 0.20
            totals.setdefault(map_name, []).append(reward)
    return {
        "source": map_stats_path,
        "mode": "map_stats_prior_bandit",
        "map_rewards": {name: sum(values) / len(values) for name, values in sorted(totals.items())},
        "action_rewards": {"pick": 0.05, "ban": -0.03},
        "exploration": 0.20,
    }


def render_report(mode: str, payload: dict[str, object]) -> str:
    lines = [
        "# Contextual Bandit Veto Policy",
        "",
        f"- 模式：`{mode}`",
        f"- exploration: {payload.get('exploration', 0.20)}",
        f"- Major 修正权重：{payload.get('major_correction_weight', 0.0)}",
        f"- 近 4 个月动作行数：{payload.get('recent_example_count', payload.get('example_count', 0))}",
        f"- Major 动作行数：{payload.get('major_example_count', 0)}",
        "",
        "## Map Rewards",
        "",
        "| 地图 | reward prior |",
        "|---|---:|",
    ]
    rewards = payload.get("map_rewards", {})
    if isinstance(rewards, dict):
            for name, value in sorted(rewards.items()):
                lines.append(f"| {name} | {float(value):+.3f} |")
    corrections = payload.get("major_map_corrections", {})
    if isinstance(corrections, dict) and corrections:
        lines.extend(
            [
                "",
                "## Major 修正",
                "",
                "| 地图 | Major 修正 |",
                "|---|---:|",
            ]
        )
        for name, value in sorted(corrections.items()):
            lines.append(f"| {name} | {float(value):+.3f} |")
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "如果同时输入近 4 个月真实 veto action CSV 和 Major veto action CSV，策略会先用近 4 个月 BO3 学基础地图倾向，再用 Major 数据生成额外修正；如果只输入一份真实序列，则学习单层 action/map 经验奖励。当前策略仍是轻量上下文选择策略，不是完整博弈树。",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
