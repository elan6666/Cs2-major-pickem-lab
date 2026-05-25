from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .collect_bo3_dataset import normalize_name


MAP_TO_DE = {
    "Ancient": "de_ancient",
    "Anubis": "de_anubis",
    "Dust2": "de_dust2",
    "Inferno": "de_inferno",
    "Mirage": "de_mirage",
    "Nuke": "de_nuke",
    "Overpass": "de_overpass",
    "Train": "de_train",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply manually verified ordered veto supplements to BO3 CSV outputs")
    parser.add_argument("--matches", required=True)
    parser.add_argument("--maps", required=True)
    parser.add_argument("--actions", required=True)
    parser.add_argument("--supplement", required=True)
    parser.add_argument("--output-matches", required=True)
    parser.add_argument("--output-maps", required=True)
    parser.add_argument("--output-actions", required=True)
    parser.add_argument("--report", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    match_rows = load_rows(args.matches)
    map_rows = load_rows(args.maps)
    action_rows = load_rows(args.actions)
    supplements = {row["slug"]: row for row in load_rows(args.supplement)}
    supplemented = apply_to_matches(match_rows, supplements)
    apply_to_maps(map_rows, supplements)
    action_rows = [row for row in action_rows if row.get("slug") not in supplements]
    action_rows.extend(build_supplement_actions(match_rows, map_rows, supplements))
    action_rows.sort(key=lambda row: (row.get("start_date", ""), row.get("slug", ""), int(row.get("order") or 0)))

    write_rows(args.output_matches, match_rows)
    write_rows(args.output_maps, map_rows)
    write_rows(args.output_actions, action_rows)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(render_report(args.supplement, supplemented, match_rows, map_rows, action_rows), encoding="utf-8")
    print(f"Applied {supplemented} veto supplements")
    return 0


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def apply_to_matches(rows: list[dict[str, str]], supplements: dict[str, dict[str, str]]) -> int:
    count = 0
    for row in rows:
        supplement = supplements.get(row.get("slug", ""))
        if not supplement:
            continue
        row["veto_sequence"] = supplement["veto_sequence"]
        row["veto_source_note"] = f"HLTV match page supplement: {supplement['hltv_url']}"
        count += 1
    return count


def apply_to_maps(rows: list[dict[str, str]], supplements: dict[str, dict[str, str]]) -> None:
    for row in rows:
        supplement = supplements.get(row.get("slug", ""))
        if not supplement:
            continue
        row["veto_sequence"] = supplement["veto_sequence"]
        row["veto_source_note"] = f"HLTV match page supplement: {supplement['hltv_url']}"


def build_supplement_actions(
    match_rows: list[dict[str, str]],
    map_rows: list[dict[str, str]],
    supplements: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    match_by_slug = {row["slug"]: row for row in match_rows}
    maps_by_slug: dict[str, dict[str, dict[str, str]]] = {}
    for row in map_rows:
        maps_by_slug.setdefault(row["slug"], {})[row["map_name"]] = row
    output: list[dict[str, str]] = []
    for slug, supplement in supplements.items():
        match = match_by_slug.get(slug)
        if not match:
            continue
        for action in parse_sequence(supplement["veto_sequence"]):
            map_row = maps_by_slug.get(slug, {}).get(action["map_name"], {})
            team = action["team"]
            map_won = ""
            match_won = ""
            if team and map_row.get("winner"):
                map_won = bool_text(normalize_name(team) == normalize_name(map_row["winner"]))
            if team and match.get("winner"):
                match_won = bool_text(normalize_name(team) == normalize_name(match["winner"]))
            reward = "0.500"
            if action["action"] == "pick" and map_won:
                reward = "1.000" if map_won == "true" else "0.000"
            elif action["action"] == "ban" and match_won:
                reward = "1.000" if match_won == "true" else "0.000"
            output.append(
                {
                    "dataset": match.get("dataset", ""),
                    "match_id": match.get("match_id", ""),
                    "slug": slug,
                    "source_url": supplement["hltv_url"],
                    "start_date": match.get("start_date", ""),
                    "order": str(action["order"]),
                    "team_id": team_id_for_name(match, team),
                    "team": team,
                    "opponent": opponent_for_name(match, team),
                    "action": action["action"],
                    "choice_type": action["choice_type"],
                    "map": action["map"],
                    "map_name": action["map_name"],
                    "game_id": map_row.get("game_id", ""),
                    "map_won": map_won,
                    "match_won": match_won,
                    "reward": reward,
                    "source_note": "HLTV match page ordered veto supplement.",
                }
            )
    return output


def parse_sequence(value: str) -> list[dict[str, str | int]]:
    output: list[dict[str, str | int]] = []
    for index, part in enumerate(value.split(" | "), start=1):
        if " was left over" in part or " left over" in part:
            map_name = part.replace(" was left over", "").replace(" left over", "").strip()
            output.append({"order": index, "team": "", "action": "leftover", "choice_type": "3", "map": map_name, "map_name": MAP_TO_DE[map_name]})
            continue
        if " removed " in part:
            team, map_name = part.split(" removed ", 1)
            output.append({"order": index, "team": team.strip(), "action": "ban", "choice_type": "2", "map": map_name.strip(), "map_name": MAP_TO_DE[map_name.strip()]})
            continue
        if " picked " in part:
            team, map_name = part.split(" picked ", 1)
            output.append({"order": index, "team": team.strip(), "action": "pick", "choice_type": "1", "map": map_name.strip(), "map_name": MAP_TO_DE[map_name.strip()]})
            continue
        raise ValueError(f"Cannot parse veto action: {part}")
    return output


def team_id_for_name(match: dict[str, str], team: str) -> str:
    if not team:
        return ""
    if normalize_name(team) == normalize_name(match.get("team1", "")):
        return match.get("team1_id", "")
    if normalize_name(team) == normalize_name(match.get("team2", "")):
        return match.get("team2_id", "")
    return ""


def opponent_for_name(match: dict[str, str], team: str) -> str:
    if not team:
        return ""
    if normalize_name(team) == normalize_name(match.get("team1", "")):
        return match.get("team2", "")
    if normalize_name(team) == normalize_name(match.get("team2", "")):
        return match.get("team1", "")
    return ""


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def render_report(
    supplement_path: str,
    supplemented: int,
    match_rows: list[dict[str, str]],
    map_rows: list[dict[str, str]],
    action_rows: list[dict[str, str]],
) -> str:
    match_blanks = sum(1 for row in match_rows if not row.get("veto_sequence"))
    map_blanks = sum(1 for row in map_rows if not row.get("veto_sequence"))
    return "\n".join(
        [
            "# Veto Supplement Application",
            "",
            f"- Supplement: `{supplement_path}`",
            f"- Supplemented matches: `{supplemented}`",
            f"- Match rows still missing veto: `{match_blanks}`",
            f"- Map rows still missing veto: `{map_blanks}`",
            f"- Veto action rows after supplement: `{len(action_rows)}`",
            "",
            "## Source Policy",
            "",
            "Supplements are only used where BO3.gg match detail had no ordered `match_maps`. Each supplement row points to an HLTV match page that displays the numbered veto sequence.",
        ]
    ) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
