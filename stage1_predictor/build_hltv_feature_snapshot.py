from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from .hltv_data import HltvTeamMetric, load_hltv_team_metrics
from .io import load_teams
from .snapshots import parse_date
from .vrs import load_stage_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a Stage 1 feature snapshot from HLTV-derived team metrics")
    parser.add_argument("--teams", required=True, help="Stage teams CSV")
    parser.add_argument("--config", required=True, help="Stage config JSON")
    parser.add_argument("--hltv-team-stats", required=True, help="Cached HLTV team stats text/HTML/CSV")
    parser.add_argument("--output", required=True, help="Output advanced feature snapshot CSV")
    parser.add_argument("--prediction-cutoff", help="Override prediction cutoff date")
    parser.add_argument("--feature-window-start", help="Override feature window start date")
    parser.add_argument("--feature-window-end", help="Override feature window end date")
    parser.add_argument("--strict", action="store_true", help="Fail if any team lacks HLTV metrics")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_hltv_feature_snapshot(
        teams_csv=args.teams,
        config_path=args.config,
        hltv_team_stats_path=args.hltv_team_stats,
        output_path=args.output,
        prediction_cutoff=args.prediction_cutoff,
        feature_window_start=args.feature_window_start,
        feature_window_end=args.feature_window_end,
        strict=args.strict,
    )
    print(f"Wrote HLTV feature snapshot to {args.output}")
    return 0


def build_hltv_feature_snapshot(
    teams_csv: str | Path,
    config_path: str | Path,
    hltv_team_stats_path: str | Path,
    output_path: str | Path,
    prediction_cutoff: str | None = None,
    feature_window_start: str | None = None,
    feature_window_end: str | None = None,
    strict: bool = False,
) -> None:
    teams = load_teams(teams_csv)
    config = load_stage_config(config_path)
    cutoff = prediction_cutoff or str(config["prediction_cutoff"])
    window_start = feature_window_start or str(config.get("feature_window_start") or cutoff)
    window_end = feature_window_end or str(config.get("feature_window_end") or cutoff)
    validate_feature_window(window_start, window_end, cutoff)

    metrics = load_hltv_team_metrics(hltv_team_stats_path, [team.name for team in teams])
    missing = [team.name for team in teams if team.name not in metrics]
    if strict and missing:
        raise ValueError(f"Missing HLTV metrics for teams: {', '.join(missing)}")

    event_id = str(config["event_id"])
    stage_id = str(config.get("stage_id") or "stage1")
    label_window_start = str(config.get("label_window_start") or "")
    label_window_end = str(config.get("label_window_end") or "")
    sample_weight = str(config.get("sample_weight") or "1.0")
    format_type = str(config.get("format_type") or "new_32_team_stage1")
    game_version = str(config.get("game_version") or "CS2")
    round_system = str(config.get("round_system") or "swiss_16_3win_3loss")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "event_id",
        "stage_id",
        "prediction_cutoff",
        "feature_window_start",
        "feature_window_end",
        "feature_date",
        "team",
        "seed",
        "region",
        "score",
        "vrs_points",
        "hltv_maps",
        "hltv_kd_diff",
        "hltv_kd",
        "hltv_rating3",
        "hltv_source_type",
        "recent_form_score",
        "map_pool_score",
        "opponent_quality_score",
        "veto_score",
        "roster_stability_score",
        "lan_score",
        "sample_confidence",
        "sample_size_penalty",
        "feature_score",
        "label_window_start",
        "label_window_end",
        "sample_weight",
        "format_type",
        "game_version",
        "round_system",
        "source",
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for team in teams:
            metric = metrics.get(team.name)
            row = build_feature_row(event_id, stage_id, cutoff, window_start, window_end, team, metric, hltv_team_stats_path)
            row.update(
                {
                    "label_window_start": label_window_start,
                    "label_window_end": label_window_end,
                    "sample_weight": sample_weight,
                    "format_type": format_type,
                    "game_version": game_version,
                    "round_system": round_system,
                }
            )
            writer.writerow(row)


def validate_feature_window(window_start: str, window_end: str, cutoff: str) -> None:
    start = parse_date(window_start)
    end = parse_date(window_end)
    cutoff_date = parse_date(cutoff)
    if start > end:
        raise ValueError("feature_window_start is after feature_window_end")
    if end > cutoff_date:
        raise ValueError("feature_window_end is after prediction_cutoff")


def build_feature_row(
    event_id: str,
    stage_id: str,
    cutoff: str,
    window_start: str,
    window_end: str,
    team,
    metric: HltvTeamMetric | None,
    source_path: str | Path,
) -> dict[str, str]:
    if metric:
        sample_confidence = min(1.0, metric.maps / 80.0)
        sample_size_penalty = max(0.0, 1.0 - sample_confidence) * 35.0
        kd_component = ((metric.kd or 1.0) - 1.0) * 150.0
        rating_component = (metric.rating - 1.0) * 300.0
        volume_component = sample_confidence * 20.0
        feature_score = team.score + rating_component + kd_component + volume_component - sample_size_penalty
        recent_form_score = (metric.rating - 1.0) * 100.0
        hltv_maps = str(metric.maps)
        hltv_kd_diff = "" if metric.kd_diff is None else str(metric.kd_diff)
        hltv_kd = "" if metric.kd is None else f"{metric.kd:.2f}"
        hltv_rating = f"{metric.rating:.2f}"
        source_type = metric.source_type
        sample_confidence_text = f"{sample_confidence:.3f}"
        sample_penalty_text = f"{sample_size_penalty:.2f}"
    else:
        feature_score = team.score - 35.0
        recent_form_score = 0.0
        hltv_maps = ""
        hltv_kd_diff = ""
        hltv_kd = ""
        hltv_rating = ""
        source_type = "missing"
        sample_confidence_text = "0.000"
        sample_penalty_text = "35.00"

    return {
        "event_id": event_id,
        "stage_id": stage_id,
        "prediction_cutoff": cutoff,
        "feature_window_start": window_start,
        "feature_window_end": window_end,
        "feature_date": window_end,
        "team": team.name,
        "seed": str(team.seed),
        "region": team.region,
        "score": f"{team.score:.0f}",
        "vrs_points": f"{team.score:.0f}",
        "hltv_maps": hltv_maps,
        "hltv_kd_diff": hltv_kd_diff,
        "hltv_kd": hltv_kd,
        "hltv_rating3": hltv_rating,
        "hltv_source_type": source_type,
        "recent_form_score": f"{recent_form_score:.2f}",
        "map_pool_score": "",
        "opponent_quality_score": "",
        "veto_score": "",
        "roster_stability_score": "",
        "lan_score": "",
        "sample_confidence": sample_confidence_text,
        "sample_size_penalty": sample_penalty_text,
        "feature_score": f"{feature_score:.2f}",
        "source": str(source_path),
    }


if __name__ == "__main__":
    raise SystemExit(main())
