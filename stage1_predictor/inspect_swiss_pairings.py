from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from .io import load_locked_results, load_teams
from .models import TeamState
from .swiss import apply_result, difficulty_score, pair_round, record_key, sort_group


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect the next Swiss-round pairings after fixed results")
    parser.add_argument("--teams", required=True, help="Stage teams CSV")
    parser.add_argument("--locked-results", help="CSV with columns round,winner,loser,best_of")
    parser.add_argument("--report", help="Optional Markdown report path")
    parser.add_argument("--json", help="Optional JSON report path")
    return parser


def build_snapshot(teams_path: str | Path, locked_results_path: str | Path | None) -> dict[str, object]:
    teams = load_teams(teams_path)
    states = {team.name: TeamState(team=team) for team in teams}
    locked_results = load_locked_results(locked_results_path)
    for result in locked_results:
        apply_result(states, result)

    all_states = list(states.values())
    active = [state for state in all_states if state.active]
    next_round = max((state.wins + state.losses for state in active), default=0) + 1
    groups: dict[tuple[int, int], list[TeamState]] = defaultdict(list)
    for state in active:
        groups[state.record].append(state)

    group_rows: list[dict[str, object]] = []
    for record in sorted(groups, key=lambda item: (-item[0], item[1])):
        ordered = sort_group(groups[record], all_states)
        group_rows.append(
            {
                "record": record_key(record),
                "teams": [
                    {
                        "team": state.team.name,
                        "seed": state.team.seed,
                        "buchholz": difficulty_score(state, all_states),
                        "opponents": sorted(state.opponents),
                    }
                    for state in ordered
                ],
            }
        )

    pairings = [
        {
            "record": record_key(left.record),
            "team1": left.team.name,
            "team1_seed": left.team.seed,
            "team1_buchholz": difficulty_score(left, all_states),
            "team2": right.team.name,
            "team2_seed": right.team.seed,
            "team2_buchholz": difficulty_score(right, all_states),
        }
        for left, right in pair_round(all_states)
    ]

    return {
        "teams": str(teams_path),
        "locked_results": str(locked_results_path or ""),
        "locked_result_count": len(locked_results),
        "next_round": next_round,
        "groups": group_rows,
        "pairings": pairings,
        "rule_notes": [
            "首轮按 1-9、2-10、...、8-16 配对。",
            "后续每轮先按同战绩分组，再按 Buchholz 分数降序、种子升序排序。",
            "第 4/5 轮的 6 队组使用 Valve/majors.im 的 15 行优先配对表，并避免重复交手。",
            "非 6 队组在前 3 轮取第一个合法高低配；后 2 轮取差距分最高的合法高低配。",
        ],
    }


def render_report(snapshot: dict[str, object]) -> str:
    lines = [
        "# 瑞士轮配对检查",
        "",
        f"- teams: `{snapshot['teams']}`",
        f"- locked_results: `{snapshot['locked_results']}`",
        f"- 已锁定赛果数：{snapshot['locked_result_count']}",
        f"- 下一轮：Round {snapshot['next_round']}",
        "",
        "## 同战绩分组",
        "",
    ]
    for group in snapshot["groups"]:  # type: ignore[index]
        lines.extend([f"### {group['record']}", "", "| 队伍 | 种子 | Buchholz | 已交手 |", "|---|---:|---:|---|"])
        for row in group["teams"]:
            lines.append(
                "| {team} | {seed} | {buchholz} | {opponents} |".format(
                    team=row["team"],
                    seed=row["seed"],
                    buchholz=row["buchholz"],
                    opponents=", ".join(row["opponents"]),
                )
            )
        lines.append("")

    lines.extend(["## 下一轮配对", "", "| 战绩组 | 队伍 A | 队伍 B |", "|---|---|---|"])
    for pairing in snapshot["pairings"]:  # type: ignore[index]
        lines.append(
            "| {record} | {team1} #{team1_seed} B{team1_buchholz} | {team2} #{team2_seed} B{team2_buchholz} |".format(
                **pairing
            )
        )
    lines.extend(["", "## 规则口径", ""])
    lines.extend(f"- {note}" for note in snapshot["rule_notes"])  # type: ignore[index]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    snapshot = build_snapshot(args.teams, args.locked_results)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(render_report(snapshot), encoding="utf-8")
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(render_report(snapshot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
