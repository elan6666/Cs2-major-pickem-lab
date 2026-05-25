from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from .collect_bo3_dataset import normalize_name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert BO3 map results and aggregate map-pool rows into map_veto stats")
    parser.add_argument("--maps", required=True, help="BO3 map rows CSV")
    parser.add_argument("--team-map-veto", required=True, help="BO3 team map_pool aggregate CSV")
    parser.add_argument("--output", required=True, help="map_veto-compatible CSV")
    parser.add_argument("--report", required=True, help="Markdown report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = build_map_stats(load_rows(args.maps), load_rows(args.team_map_veto))
    write_rows(args.output, rows)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(args.output, rows), encoding="utf-8")
    print(f"Wrote {len(rows)} BO3 map-stat rows to {args.output}")
    return 0


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"CSV is empty: {path}")
    return rows


def build_map_stats(map_rows: list[dict[str, str]], veto_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    team_names = {normalize_name(row["team"]): row["team"] for row in veto_rows if row.get("team")}
    played: dict[tuple[str, str], int] = defaultdict(int)
    wins: dict[tuple[str, str], int] = defaultdict(int)
    for row in map_rows:
        map_name = row.get("map_name", "")
        winner = normalize_name(row.get("winner", ""))
        for side in ("team1", "team2"):
            team = row.get(side, "")
            key = normalize_name(team)
            if key not in team_names:
                continue
            stat_key = (team_names[key], map_name)
            played[stat_key] += 1
            if key == winner:
                wins[stat_key] += 1

    pick_totals: dict[str, float] = defaultdict(float)
    ban_totals: dict[str, float] = defaultdict(float)
    raw_pool: dict[tuple[str, str], dict[str, str]] = {}
    for row in veto_rows:
        team = row.get("team", "")
        map_name = row.get("map_name", "")
        if not team or not map_name:
            continue
        raw_pool[(team, map_name)] = row
        pick_totals[team] += number(row.get("picked_maps"))
        ban_totals[team] += number(row.get("banned_maps"))

    output: list[dict[str, str]] = []
    for team, map_name in sorted(set(played) | set(raw_pool)):
        pool = raw_pool.get((team, map_name), {})
        maps_played = played.get((team, map_name), int(number(pool.get("maps_count"))))
        win_rate = (wins.get((team, map_name), 0) / maps_played * 100.0) if maps_played else 50.0
        picked = number(pool.get("picked_maps"))
        banned = number(pool.get("banned_maps"))
        output.append(
            {
                "team": team,
                "map": map_name,
                "win_rate": f"{win_rate:.2f}",
                "maps_played": str(maps_played),
                "pick_rate": f"{rate(picked, pick_totals[team]):.2f}",
                "ban_rate": f"{rate(banned, ban_totals[team]):.2f}",
                "pistol_win_rate": "",
                "first_kill_round_win_rate": "",
                "first_death_round_win_rate": "",
                "source": "bo3.gg match maps + team map_pool aggregate",
            }
        )
    return output


def number(value: str | None) -> float:
    if value is None or str(value).strip() == "":
        return 0.0
    try:
        return float(str(value).strip())
    except ValueError:
        return 0.0


def rate(value: float, total: float) -> float:
    return (value / total * 100.0) if total > 0 else 0.0


def write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "team",
        "map",
        "win_rate",
        "maps_played",
        "pick_rate",
        "ban_rate",
        "pistol_win_rate",
        "first_kill_round_win_rate",
        "first_death_round_win_rate",
        "source",
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_report(output_path: str, rows: list[dict[str, str]]) -> str:
    teams = sorted({row["team"] for row in rows})
    maps = sorted({row["map"] for row in rows})
    return "\n".join(
        [
            "# BO3 Map Stats",
            "",
            f"- Output: `{output_path}`",
            f"- Teams: `{len(teams)}`",
            f"- Maps: `{len(maps)}`",
            f"- Rows: `{len(rows)}`",
            "",
            "## Notes",
            "",
            "Win rate and maps played come from BO3 map result rows. Pick/ban rates are normalized from BO3 team map_pool aggregate counts across each team's available map rows.",
        ]
    ) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
