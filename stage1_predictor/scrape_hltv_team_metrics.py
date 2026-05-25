from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

from .hltv_data import (
    FetchResult,
    HltvTeamMetric,
    fetch_hltv_page,
    load_metric_csv,
    parse_hltv_team_overview_current_roster,
    parse_hltv_team_stats,
)
from .io import load_teams


HLTV_TEAM_STATS_URL = "https://www.hltv.org/stats/teams?csVersion=CS2"
FALLBACK_TEAM_URLS = {
    "FlyQuest": "https://www.hltv.org/team/12774/flyquest",
    "THUNDER dOWNUNDER": "https://www.hltv.org/team/13486/thunder-downunder",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and parse HLTV team metrics for a Stage 1 team list")
    parser.add_argument("--teams", required=True, help="Stage teams CSV")
    parser.add_argument("--output", required=True, help="Output HLTV metric CSV")
    parser.add_argument("--raw-dir", default="data/raw/hltv", help="Directory for fetched raw HLTV pages")
    parser.add_argument("--attempt-json", help="Optional fetch-attempt JSON report")
    parser.add_argument("--source-report", help="Optional Markdown source report")
    parser.add_argument("--fallback-csv", help="Use an existing real HLTV-derived CSV for teams blocked by Cloudflare")
    parser.add_argument("--strict", action="store_true", help="Fail if any team is missing after all sources")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    teams = [team.name for team in load_teams(args.teams)]
    metrics, attempts, missing = scrape_hltv_team_metrics(
        team_names=teams,
        raw_dir=args.raw_dir,
        fallback_csv=args.fallback_csv,
    )
    if args.strict and missing:
        raise SystemExit(f"Missing HLTV metrics for teams: {', '.join(missing)}")
    write_metric_csv(args.output, teams, metrics)
    if args.attempt_json:
        write_attempt_json(args.attempt_json, attempts, missing)
    if args.source_report:
        write_source_report(args.source_report, attempts, missing, args.fallback_csv)
    print(f"Wrote {len(metrics)} HLTV metric rows to {args.output}")
    if missing:
        print(f"Missing teams: {', '.join(missing)}")
    return 0


def scrape_hltv_team_metrics(
    team_names: list[str],
    raw_dir: str | Path,
    fallback_csv: str | Path | None = None,
) -> tuple[dict[str, HltvTeamMetric], list[FetchResult], list[str]]:
    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    attempts: list[FetchResult] = []
    stats_path = raw / f"hltv_stats_teams_cs2_{today}.html"
    stats_attempt = fetch_hltv_page(HLTV_TEAM_STATS_URL, stats_path)
    attempts.append(stats_attempt)

    metrics: dict[str, HltvTeamMetric] = {}
    if not stats_attempt.blocked and Path(stats_attempt.path).exists():
        source = Path(stats_attempt.path).read_text(encoding="utf-8", errors="replace")
        metrics.update(parse_hltv_team_stats(source, team_names))

    for team in team_names:
        if team in metrics or team not in FALLBACK_TEAM_URLS:
            continue
        team_path = raw / f"hltv_team_{slugify(team)}_{today}.html"
        attempt = fetch_hltv_page(FALLBACK_TEAM_URLS[team], team_path)
        attempts.append(attempt)
        if attempt.blocked or not Path(attempt.path).exists():
            continue
        source = Path(attempt.path).read_text(encoding="utf-8", errors="replace")
        metric = parse_hltv_team_overview_current_roster(source, team)
        if metric:
            metrics[team] = metric

    if fallback_csv:
        fallback_metrics = load_metric_csv(fallback_csv)
        for team in team_names:
            if team not in metrics and team in fallback_metrics:
                metrics[team] = fallback_metrics[team]

    missing = [team for team in team_names if team not in metrics]
    return metrics, attempts, missing


def write_metric_csv(path: str | Path, team_names: list[str], metrics: dict[str, HltvTeamMetric]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["team", "maps", "kd_diff", "kd", "rating3", "source_type", "source_url"],
        )
        writer.writeheader()
        for team in team_names:
            metric = metrics.get(team)
            if not metric:
                continue
            writer.writerow(
                {
                    "team": team,
                    "maps": metric.maps,
                    "kd_diff": "" if metric.kd_diff is None else metric.kd_diff,
                    "kd": "" if metric.kd is None else f"{metric.kd:.2f}",
                    "rating3": f"{metric.rating:.2f}",
                    "source_type": metric.source_type,
                    "source_url": metric.source_url or FALLBACK_TEAM_URLS.get(team, HLTV_TEAM_STATS_URL),
                }
            )


def write_attempt_json(path: str | Path, attempts: list[FetchResult], missing: list[str]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": date.today().isoformat(),
        "attempts": [attempt.__dict__ for attempt in attempts],
        "missing": missing,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_source_report(
    path: str | Path,
    attempts: list[FetchResult],
    missing: list[str],
    fallback_csv: str | Path | None,
) -> None:
    lines = [
        "# HLTV Data Sources",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## Source Pages",
        "",
        f"- HLTV team stats, CS2 all time: `{HLTV_TEAM_STATS_URL}`",
    ]
    for team, url in FALLBACK_TEAM_URLS.items():
        lines.append(f"- {team} team overview: `{url}`")
    lines.extend(["", "## Local Fetch Attempts", ""])
    for attempt in attempts:
        status = "blocked" if attempt.blocked else attempt.message
        lines.append(f"- `{attempt.url}` -> status={attempt.status_code}, result={status}, path=`{attempt.path}`")
    if fallback_csv:
        lines.extend(["", "## Fallback Cache", "", f"- Used existing HLTV-derived cache: `{fallback_csv}`"])
    if missing:
        lines.extend(["", "## Missing Teams", "", "- " + ", ".join(missing)])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


if __name__ == "__main__":
    raise SystemExit(main())
