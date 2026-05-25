from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


BO3_API = "https://api.bo3.gg/api/v1"
BO3_WEB = "https://bo3.gg"
VALVE_RAW = (
    "https://raw.githubusercontent.com/ValveSoftware/"
    "counter-strike_regional_standings/main/invitation/2026/"
)
USER_AGENT = "Codex data collection for local CS2 research"

STAGE_TEAM_SLUGS = {
    "GamerLegion": ["gamerlegion", "gamer-legion"],
    "B8": ["b8"],
    "HEROIC": ["heroic"],
    "BetBoom": ["betboom", "betboom-team"],
    "BIG": ["big"],
    "M80": ["m80-cs-go", "m80"],
    "MIBR": ["mibr"],
    "SINNERS": ["sinners"],
    "NRG": ["nrg"],
    "TYLOO": ["tyloo-cs-go", "tyloo"],
    "Sharks": ["sharks"],
    "Gaimin Gladiators": ["gaimingladiators", "gaimin-gladiators-1", "gaimin-gladiators"],
    "Liquid": ["liquid"],
    "Lynn Vision": ["lynn-vision"],
    "THUNDER dOWNUNDER": ["thuneder-downunder", "thunder-downunder", "thunder-downunder-cs-go"],
    "FlyQuest": ["flyquest"],
}

MAJOR_TOURNAMENTS = {
    "blast_austin_major_2025": [
        ("blast_austin_major_2025_stage1", "blast-tv-austin-major-2025-stage-1"),
        ("blast_austin_major_2025_stage2", "blast-tv-austin-major-2025-stage-2"),
        ("blast_austin_major_2025_stage3_playoffs", "blast-tv-austin-major-2025"),
    ],
    "starladder_budapest_major_2025": [
        ("starladder_budapest_major_2025_stage1", "starladder-budapest-major-2025-stage-1"),
        ("starladder_budapest_major_2025_stage2", "starladder-budapest-major-2025-stage-2"),
        ("starladder_budapest_major_2025_stage3_playoffs", "starladder-budapest-major-2025"),
    ],
}


@dataclass(frozen=True)
class TeamInfo:
    source_name: str
    id: int
    slug: str
    name: str
    rank: int | None


def normalize_name(value: str) -> str:
    text = value.lower().replace("&", "and")
    text = re.sub(r"\b(team|gaming|esports|e-sports|club)\b", " ", text)
    text = text.replace("mousesports", "mouz")
    text = text.replace("thunder downunder", "thunder downunder")
    return re.sub(r"[^a-z0-9]+", "", text)


def request_json(path: str, params: dict[str, str] | None = None, cache_path: Path | None = None) -> Any:
    url = path if path.startswith("http") else f"{BO3_API}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    time.sleep(0.12)
    return payload


def fetch_text(url: str, output: Path | None = None) -> str:
    if output and output.exists():
        return output.read_text(encoding="utf-8")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        text = response.read().decode("utf-8")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    return text


def parse_vrs_top100(markdown: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"^\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
    for rank, points, name in pattern.findall(markdown):
        rank_int = int(rank)
        if rank_int > 100:
            continue
        clean = name.strip()
        rows[normalize_name(clean)] = {"vrs_rank": str(rank_int), "vrs_points": points, "vrs_name": clean}
    return rows


def load_stage_teams(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [row["team"] for row in csv.DictReader(handle)]


def resolve_team(team: str, cache_dir: Path) -> TeamInfo:
    errors: list[str] = []
    for slug in STAGE_TEAM_SLUGS.get(team, [slugify(team)]):
        try:
            payload = request_json(f"/teams/{slug}", cache_path=cache_dir / "teams" / f"{slug}.json")
            return TeamInfo(
                source_name=team,
                id=int(payload["id"]),
                slug=payload["slug"],
                name=payload["name"],
                rank=payload.get("rank"),
            )
        except Exception as exc:  # noqa: BLE001 - keep trying slug aliases and report all failures.
            errors.append(f"{slug}: {exc}")
    raise RuntimeError(f"Could not resolve BO3 team for {team}: {'; '.join(errors)}")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def fetch_matches(
    cache_dir: Path,
    *,
    team_id: int | None = None,
    tournament_id: int | None = None,
    start_from: str | None = None,
    start_to: str | None = None,
    label: str,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    offset = 0
    limit = 100
    while True:
        filters = {
            "with": "teams,tournament,games",
            "join": "tournaments_deep",
            "filter[matches.discipline_id][eq]": "1",
            "filter[matches.status][in]": "finished",
            "page[limit]": str(limit),
            "page[offset]": str(offset),
            "sort": "-start_date",
        }
        if team_id is not None:
            filters["filter[matches.team_ids][overlap]"] = str(team_id)
        if tournament_id is not None:
            filters["filter[matches.tournament_id][in]"] = str(tournament_id)
        if start_from:
            filters["filter[matches.start_date][gt]"] = start_from
        if start_to:
            filters["filter[matches.start_date][lt]"] = start_to
        payload = request_json("/matches", filters, cache_dir / "matches" / f"{label}_{offset}.json")
        results = payload.get("results", [])
        matches.extend(results)
        total = payload.get("total", {})
        if offset + limit >= int(total.get("count", len(matches))):
            break
        offset += limit
    return matches


def fetch_team_map_pool(team: TeamInfo, cache_dir: Path, start_from: str, start_to: str) -> list[dict[str, Any]]:
    params = {
        "filter[begin_at_from]": start_from,
        "filter[begin_at_to]": start_to,
    }
    payload = request_json(
        f"/teams/{team.slug}/map_pool",
        params,
        cache_dir / "map_pool" / f"{team.slug}_{start_from}_{start_to}.json",
    )
    rows = payload.values() if isinstance(payload, dict) else payload
    return [row for row in rows if row.get("maps_count") or row.get("picked_maps") or row.get("banned_maps")]


def fetch_tournament(slug: str, cache_dir: Path) -> dict[str, Any]:
    return request_json(f"/tournaments/{slug}", cache_path=cache_dir / "tournaments" / f"{slug}.json")


def fetch_match_detail(match: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    slug = str(match.get("slug", "")).strip()
    if not slug:
        return {}
    return request_json(f"/matches/{slug}", cache_path=cache_dir / "match_details" / f"{slug}.json")


def match_source_url(match: dict[str, Any]) -> str:
    return f"{BO3_WEB}/matches/{match['slug']}"


def compact_team(team: dict[str, Any] | None) -> dict[str, Any]:
    if not team:
        return {"id": "", "slug": "", "name": "", "rank": ""}
    return {
        "id": team.get("id", ""),
        "slug": team.get("slug", ""),
        "name": team.get("name", ""),
        "rank": team.get("rank", ""),
    }


def choice_type_to_action(value: Any) -> str:
    try:
        choice_type = int(value)
    except (TypeError, ValueError):
        return ""
    return {1: "pick", 2: "ban", 3: "leftover"}.get(choice_type, "")


def veto_map_name(row: dict[str, Any]) -> tuple[str, str]:
    maps = row.get("maps") or {}
    display = str(maps.get("name") or maps.get("map_name") or "").strip()
    normalized = str(maps.get("map_name") or display).strip()
    return display, normalized


def match_veto_rows(match: dict[str, Any]) -> list[dict[str, Any]]:
    detail = match.get("_detail") if isinstance(match.get("_detail"), dict) else match
    rows = detail.get("match_maps") if isinstance(detail, dict) else None
    if not rows:
        rows = match.get("match_maps") or []
    return sorted(rows, key=lambda row: int(row.get("order") or 0))


def render_veto_sequence(match: dict[str, Any]) -> str:
    parts: list[str] = []
    for row in match_veto_rows(match):
        action = choice_type_to_action(row.get("choice_type"))
        display, _normalized = veto_map_name(row)
        team = compact_team(row.get("teams"))["name"]
        if not action or not display:
            continue
        if action == "leftover":
            parts.append(f"{display} left over")
        elif team:
            verb = "remove" if action == "ban" else "pick"
            parts.append(f"{team} {verb} {display}")
    return " | ".join(parts)


def team_names_for_match(match: dict[str, Any]) -> tuple[str, str]:
    team1 = str(compact_team(match.get("team1"))["name"])
    team2 = str(compact_team(match.get("team2"))["name"])
    return team1, team2


def opponent_for_team(match: dict[str, Any], team_id: str, team_name: str) -> str:
    team1 = compact_team(match.get("team1"))
    team2 = compact_team(match.get("team2"))
    if team_id and str(team1["id"]) == team_id:
        return str(team2["name"])
    if team_id and str(team2["id"]) == team_id:
        return str(team1["name"])
    team1_name, team2_name = team_names_for_match(match)
    if normalize_name(team_name) == normalize_name(team1_name):
        return team2_name
    if normalize_name(team_name) == normalize_name(team2_name):
        return team1_name
    return ""


def game_by_map(match: dict[str, Any]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for game in match.get("games") or []:
        map_name = str(game.get("map_name") or "").strip()
        if map_name:
            output[map_name] = game
    return output


def bool_text(value: bool | None) -> str:
    if value is None:
        return ""
    return "true" if value else "false"


def flatten_veto_actions(match: dict[str, Any], dataset: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    games = game_by_map(match)
    winner = compact_team(match.get("winner_team"))
    winner_id = str(winner["id"])
    winner_name = str(winner["name"])
    for row in match_veto_rows(match):
        order = str(row.get("order", ""))
        team = compact_team(row.get("teams"))
        team_id = str(row.get("team_id") or team["id"] or "")
        team_name = str(team["name"])
        action = choice_type_to_action(row.get("choice_type"))
        display_map, normalized_map = veto_map_name(row)
        game = games.get(normalized_map, {})
        map_winner = str(game.get("winner_clan_name") or "")
        map_won: bool | None = None
        match_won: bool | None = None
        if team_name and map_winner:
            map_won = normalize_name(team_name) == normalize_name(map_winner)
        if team_id and winner_id:
            match_won = team_id == winner_id
        elif team_name and winner_name:
            match_won = normalize_name(team_name) == normalize_name(winner_name)
        reward = 0.5
        if action == "pick" and map_won is not None:
            reward = 1.0 if map_won else 0.0
        elif action == "ban" and match_won is not None:
            reward = 1.0 if match_won else 0.0
        output.append(
            {
                "dataset": dataset,
                "match_id": str(match.get("id", "")),
                "slug": str(match.get("slug", "")),
                "source_url": match_source_url(match),
                "start_date": str(match.get("start_date", "")),
                "order": order,
                "team_id": team_id,
                "team": team_name,
                "opponent": opponent_for_team(match, team_id, team_name),
                "action": action,
                "choice_type": str(row.get("choice_type", "")),
                "map": display_map,
                "map_name": normalized_map,
                "game_id": str(row.get("game_id") or game.get("id") or ""),
                "map_won": bool_text(map_won),
                "match_won": bool_text(match_won),
                "reward": f"{reward:.3f}",
                "source_note": "BO3 match detail endpoint match_maps; choice_type 1=pick, 2=ban/remove, 3=leftover/decider.",
            }
        )
    return output


def flatten_match(match: dict[str, Any], dataset: str, vrs_top100: dict[str, dict[str, str]] | None = None) -> dict[str, str]:
    team1 = compact_team(match.get("team1"))
    team2 = compact_team(match.get("team2"))
    winner = compact_team(match.get("winner_team"))
    tournament = match.get("tournament") or {}
    team1_vrs = (vrs_top100 or {}).get(normalize_name(str(team1["name"])), {})
    team2_vrs = (vrs_top100 or {}).get(normalize_name(str(team2["name"])), {})
    veto_sequence = render_veto_sequence(match)
    return {
        "dataset": dataset,
        "match_id": str(match.get("id", "")),
        "slug": str(match.get("slug", "")),
        "source_url": match_source_url(match),
        "start_date": str(match.get("start_date", "")),
        "end_date": str(match.get("end_date", "")),
        "status": str(match.get("status", "")),
        "bo_type": str(match.get("bo_type", "")),
        "tier": str(match.get("tier", "")),
        "tier_rank": str(match.get("tier_rank", "")),
        "team1_id": str(team1["id"]),
        "team1": str(team1["name"]),
        "team1_rank_bo3": str(team1["rank"]),
        "team1_vrs_rank": team1_vrs.get("vrs_rank", ""),
        "team1_vrs_points": team1_vrs.get("vrs_points", ""),
        "team2_id": str(team2["id"]),
        "team2": str(team2["name"]),
        "team2_rank_bo3": str(team2["rank"]),
        "team2_vrs_rank": team2_vrs.get("vrs_rank", ""),
        "team2_vrs_points": team2_vrs.get("vrs_points", ""),
        "winner_team_id": str(winner["id"]),
        "winner": str(winner["name"]),
        "team1_score": str(match.get("team1_score", "")),
        "team2_score": str(match.get("team2_score", "")),
        "tournament_id": str(tournament.get("id", match.get("tournament_id", ""))),
        "tournament": str(tournament.get("name", "")),
        "tournament_slug": str(tournament.get("slug", "")),
        "veto_sequence": veto_sequence,
        "veto_source_note": (
            "BO3 match detail endpoint exposes ordered match_maps veto sequence."
            if veto_sequence
            else "No ordered match_maps veto sequence found in BO3 match detail payload."
        ),
    }


def flatten_maps(match: dict[str, Any], dataset: str) -> list[dict[str, str]]:
    team1 = compact_team(match.get("team1"))
    team2 = compact_team(match.get("team2"))
    veto_sequence = render_veto_sequence(match)
    rows: list[dict[str, str]] = []
    for game in sorted(match.get("games") or [], key=lambda row: row.get("number") or 0):
        if not game.get("map_name") or game.get("status") != "finished":
            continue
        winner = str(game.get("winner_clan_name") or "")
        loser = str(game.get("loser_clan_name") or "")
        rows.append(
            {
                "dataset": dataset,
                "match_id": str(match.get("id", "")),
                "slug": str(match.get("slug", "")),
                "source_url": match_source_url(match),
                "start_date": str(match.get("start_date", "")),
                "team1": str(team1["name"]),
                "team2": str(team2["name"]),
                "map_number": str(game.get("number", "")),
                "map_name": str(game.get("map_name", "")),
                "status": str(game.get("status", "")),
                "winner": winner,
                "loser": loser,
                "winner_score": str(game.get("winner_clan_score", "")),
                "loser_score": str(game.get("loser_clan_score", "")),
                "rounds_count": str(game.get("rounds_count", "")),
                "begin_at": str(game.get("begin_at", "")),
                "veto_sequence": veto_sequence,
                "veto_source_note": (
                    "BO3 match detail endpoint exposes ordered match_maps veto sequence."
                    if veto_sequence
                    else "No ordered match_maps veto sequence found in BO3 match detail payload."
                ),
            }
        )
    return rows


def flatten_map_pool(team: TeamInfo, rows: list[dict[str, Any]], dataset: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        output.append(
            {
                "dataset": dataset,
                "team_id": str(team.id),
                "team": team.name,
                "team_slug": team.slug,
                "map_name": str(row.get("map_name") or row.get("map") or ""),
                "maps_count": str(row.get("maps_count", "")),
                "winrate": str(row.get("winrate", row.get("win_rate", ""))),
                "picked_maps": str(row.get("picked_maps", "")),
                "banned_maps": str(row.get("banned_maps", "")),
                "pick_rate": str(row.get("pick_rate", "")),
                "ban_rate": str(row.get("ban_rate", "")),
                "source_url": f"{BO3_WEB}/teams/{team.slug}",
                "source_note": "BO3 team map_pool endpoint; aggregate pick/ban counts, not per-match sequence.",
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def attach_match_details(matches: list[dict[str, Any]], cache_dir: Path) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for match in matches:
        enriched = dict(match)
        try:
            enriched["_detail"] = fetch_match_detail(match, cache_dir)
        except Exception as exc:  # noqa: BLE001 - keep the list-derived match if detail fetch fails.
            enriched["_detail_error"] = str(exc)
        output.append(enriched)
    return output


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# BO3/VRS Data Collection",
        "",
        f"- Date: `{summary['date']}`",
        f"- Recent window: `{summary['recent_start']}` to `{summary['recent_end']}`",
        f"- VRS snapshot: `{summary['vrs_snapshot']}`",
        f"- Stage teams resolved: `{summary['stage_teams_resolved']}/16`",
        f"- Recent complete matches: `{summary['recent_matches']}`",
        f"- Recent map rows: `{summary['recent_maps']}`",
        f"- Recent team-map veto rows: `{summary['recent_veto_rows']}`",
        f"- Recent per-match veto action rows: `{summary['recent_veto_action_rows']}`",
        f"- Recent matches with veto sequence: `{summary['recent_matches_with_veto']}`",
        f"- Major complete matches: `{summary['major_matches']}`",
        f"- Major map rows: `{summary['major_maps']}`",
        f"- Major per-match veto action rows: `{summary['major_veto_action_rows']}`",
        f"- Major matches with veto sequence: `{summary['major_matches_with_veto']}`",
        "",
        "## Outputs",
        "",
    ]
    lines.extend(f"- `{path}`" for path in summary["outputs"])
    lines.extend(
        [
            "",
            "## Source Notes",
            "",
            "- VRS Top 100 names/ranks come from Valve's official `counter-strike_regional_standings` snapshot.",
            "- Match and map rows come from BO3.gg public API match payloads.",
            "- Ordered per-match veto sequences come from the BO3.gg match detail `match_maps` payload. Mapping is `choice_type=1` pick, `choice_type=2` ban/remove, and `choice_type=3` leftover/decider.",
            "- BO3 also exposes aggregate team map_pool pick/ban counts, kept separately as a team-level comfort prior.",
            "- Major coverage uses Stage 1, Stage 2, and the main Stage 3/playoffs tournament entries for BLAST.tv Austin Major 2025 and StarLadder Budapest Major 2025.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect BO3 match/map and aggregate veto data for Cologne Stage 1 modeling")
    parser.add_argument("--stage-teams", default="data/iem_cologne_2026_stage1_teams.csv")
    parser.add_argument("--recent-start", default="2026-01-24")
    parser.add_argument("--recent-end", default="2026-05-24")
    parser.add_argument("--vrs-snapshot", default="2026_05_04")
    parser.add_argument("--output-dir", default="data/bo3")
    parser.add_argument("--raw-dir", default="data/raw/bo3")
    parser.add_argument("--report", help="Markdown collection report path; defaults to reports/bo3_data_collection_<date>.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    raw_dir = Path(args.raw_dir)
    stamp = date.today().isoformat()

    vrs_path = Path("data/vrs") / f"standings_global_{args.vrs_snapshot}.md"
    vrs_text = fetch_text(f"{VALVE_RAW}standings_global_{args.vrs_snapshot}.md", vrs_path)
    vrs_top100 = parse_vrs_top100(vrs_text)

    stage_teams = load_stage_teams(Path(args.stage_teams))
    team_infos = [resolve_team(team, raw_dir) for team in stage_teams]
    stage_team_ids = {team.id for team in team_infos}

    recent_matches_by_id: dict[int, dict[str, Any]] = {}
    recent_start_iso = f"{args.recent_start}T00:00:00.000Z"
    recent_end_iso = f"{args.recent_end}T23:59:59.999Z"
    for team in team_infos:
        for match in fetch_matches(
            raw_dir,
            team_id=team.id,
            start_from=recent_start_iso,
            start_to=recent_end_iso,
            label=f"recent_{team.slug}",
        ):
            team1_id = int(match.get("team1_id") or 0)
            team2_id = int(match.get("team2_id") or 0)
            if team1_id in stage_team_ids and team2_id in stage_team_ids:
                recent_matches_by_id[int(match["id"])] = match
                continue
            if team1_id in stage_team_ids:
                opponent_name = (match.get("team2") or {}).get("name", "")
            elif team2_id in stage_team_ids:
                opponent_name = (match.get("team1") or {}).get("name", "")
            else:
                continue
            if normalize_name(opponent_name) in vrs_top100:
                recent_matches_by_id[int(match["id"])] = match

    recent_veto_rows: list[dict[str, str]] = []
    for team in team_infos:
        recent_veto_rows.extend(
            flatten_map_pool(
                team,
                fetch_team_map_pool(team, raw_dir, args.recent_start, args.recent_end),
                "cologne_stage1_last4months_vs_vrs_top100",
            )
        )

    major_matches_by_id: dict[int, dict[str, Any]] = {}
    for event_id, tournaments in MAJOR_TOURNAMENTS.items():
        for stage_id, slug in tournaments:
            tournament = fetch_tournament(slug, raw_dir)
            for match in fetch_matches(raw_dir, tournament_id=int(tournament["id"]), label=f"major_{stage_id}"):
                match["_dataset"] = event_id
                major_matches_by_id[int(match["id"])] = match

    recent_matches = attach_match_details(list(recent_matches_by_id.values()), raw_dir)
    major_matches = attach_match_details(list(major_matches_by_id.values()), raw_dir)
    recent_match_rows = [
        flatten_match(match, "cologne_stage1_last4months_vs_vrs_top100", vrs_top100)
        for match in sorted(recent_matches, key=lambda row: row["start_date"])
    ]
    recent_map_rows = [
        row
        for match in sorted(recent_matches, key=lambda row: row["start_date"])
        for row in flatten_maps(match, "cologne_stage1_last4months_vs_vrs_top100")
    ]
    major_match_rows = [
        flatten_match(match, str(match.get("_dataset", "major_full")), None)
        for match in sorted(major_matches, key=lambda row: row["start_date"])
    ]
    major_map_rows = [
        row
        for match in sorted(major_matches, key=lambda row: row["start_date"])
        for row in flatten_maps(match, str(match.get("_dataset", "major_full")))
    ]
    recent_veto_action_rows = [
        row
        for match in sorted(recent_matches, key=lambda row: row["start_date"])
        for row in flatten_veto_actions(match, "cologne_stage1_last4months_vs_vrs_top100")
    ]
    major_veto_action_rows = [
        row
        for match in sorted(major_matches, key=lambda row: row["start_date"])
        for row in flatten_veto_actions(match, str(match.get("_dataset", "major_full")))
    ]

    outputs = {
        "recent_matches": output_dir / f"bo3_stage1_last4months_matches_{stamp}.csv",
        "recent_maps": output_dir / f"bo3_stage1_last4months_maps_{stamp}.csv",
        "recent_veto": output_dir / f"bo3_stage1_last4months_team_map_veto_{stamp}.csv",
        "recent_veto_actions": output_dir / f"bo3_stage1_last4months_veto_actions_{stamp}.csv",
        "major_matches": output_dir / f"bo3_major_matches_{stamp}.csv",
        "major_maps": output_dir / f"bo3_major_maps_{stamp}.csv",
        "major_veto_actions": output_dir / f"bo3_major_veto_actions_{stamp}.csv",
    }
    write_csv(outputs["recent_matches"], recent_match_rows)
    write_csv(outputs["recent_maps"], recent_map_rows)
    write_csv(outputs["recent_veto"], recent_veto_rows)
    write_csv(outputs["recent_veto_actions"], recent_veto_action_rows)
    write_csv(outputs["major_matches"], major_match_rows)
    write_csv(outputs["major_maps"], major_map_rows)
    write_csv(outputs["major_veto_actions"], major_veto_action_rows)

    summary = {
        "date": stamp,
        "recent_start": args.recent_start,
        "recent_end": args.recent_end,
        "vrs_snapshot": args.vrs_snapshot,
        "stage_teams_resolved": len(team_infos),
        "recent_matches": len(recent_match_rows),
        "recent_maps": len(recent_map_rows),
        "recent_veto_rows": len(recent_veto_rows),
        "recent_veto_action_rows": len(recent_veto_action_rows),
        "recent_matches_with_veto": sum(1 for row in recent_match_rows if row.get("veto_sequence")),
        "major_matches": len(major_match_rows),
        "major_maps": len(major_map_rows),
        "major_veto_action_rows": len(major_veto_action_rows),
        "major_matches_with_veto": sum(1 for row in major_match_rows if row.get("veto_sequence")),
        "outputs": [str(path) for path in outputs.values()],
    }
    report_path = Path(args.report or f"reports/bo3_data_collection_{stamp}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
