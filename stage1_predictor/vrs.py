from __future__ import annotations

import base64
import csv
import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .io import validate_teams
from .models import Team


@dataclass(frozen=True)
class VrsEntry:
    rank: int
    points: int
    team: str
    roster: str


def load_github_markdown(api_url: str) -> str:
    request = urllib.request.Request(api_url, headers={"User-Agent": "cs2-major-predictor/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "content" not in payload:
        raise ValueError(f"GitHub API response did not include content: {api_url}")
    return base64.b64decode(payload["content"]).decode("utf-8")


def parse_vrs_markdown(markdown: str) -> dict[str, VrsEntry]:
    entries: dict[str, VrsEntry] = {}
    pattern = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
    for line in markdown.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        rank_text, points_text, team_name, roster = match.groups()
        entry = VrsEntry(
            rank=int(rank_text),
            points=int(points_text),
            team=team_name.strip(),
            roster=roster.strip(),
        )
        existing = entries.get(entry.team)
        if existing is None or entry.rank < existing.rank:
            entries[entry.team] = entry
    return entries


def load_stage_config(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_teams_from_stage_config(config: dict[str, object]) -> list[Team]:
    cache_path = config.get("vrs_cache_path")
    if cache_path:
        markdown = Path(str(cache_path)).read_text(encoding="utf-8")
    else:
        api_url = str(config["vrs_github_api_url"])
        markdown = load_github_markdown(api_url)
    standings = parse_vrs_markdown(markdown)
    teams: list[Team] = []
    raw_team_configs = [dict(item) for item in config["teams"]]  # type: ignore[index]
    resolved_entries: list[tuple[dict[object, object], VrsEntry, str]] = []

    for team_config in raw_team_configs:
        display_name = str(team_config["team"])
        vrs_name = str(team_config.get("vrs_name") or display_name)
        if vrs_name not in standings:
            raise ValueError(f"Team not found in VRS standings: {vrs_name}")
        entry = standings[vrs_name]
        resolved_entries.append((team_config, entry, vrs_name))

    if all("seed" in team_config for team_config, _, _ in resolved_entries):
        seed_by_name = {
            str(team_config["team"]): int(team_config["seed"])
            for team_config, _, _ in resolved_entries
        }
    else:
        sorted_entries = sorted(resolved_entries, key=lambda item: item[1].rank)
        seed_by_name = {
            str(team_config["team"]): index + 1
            for index, (team_config, _, _) in enumerate(sorted_entries)
        }

    for team_config, entry, vrs_name in resolved_entries:
        display_name = str(team_config["team"])
        notes = (
            f"source={config.get('event_id')}; "
            f"prediction_cutoff={config.get('prediction_cutoff')}; "
            f"vrs_rank={entry.rank}; vrs_points={entry.points}; "
            f"vrs_name={vrs_name}"
        )
        teams.append(
            Team(
                seed=seed_by_name[display_name],
                name=display_name,
                score=float(entry.points),
                region=str(team_config.get("region", "")),
                notes=notes,
            )
        )

    validate_teams(teams)
    return sorted(teams, key=lambda team: team.seed)


def write_teams_csv(path: str | Path, teams: list[Team]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["seed", "team", "score", "region", "notes"])
        writer.writeheader()
        for team in teams:
            writer.writerow(
                {
                    "seed": team.seed,
                    "team": team.name,
                    "score": f"{team.score:.0f}",
                    "region": team.region,
                    "notes": team.notes,
                }
            )
