from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .io import load_teams
from .vrs import load_stage_config


REQUIRED_SNAPSHOT_COLUMNS = {
    "event_id",
    "stage_id",
    "team",
    "seed",
    "score",
    "region",
    "prediction_cutoff",
    "feature_window_start",
    "feature_window_end",
    "feature_date",
    "label_window_start",
    "label_window_end",
    "sample_weight",
    "format_type",
    "game_version",
    "round_system",
    "source",
}

BLOCKED_FEATURE_COLUMNS = {
    "final_record",
    "advanced",
    "went_3_0",
    "went_0_3",
    "target_event_rating",
    "post_event_rating",
    "post_event_rank",
    "post_event_map_win_rate",
}


@dataclass(frozen=True)
class SnapshotValidationResult:
    path: str
    rows: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def build_snapshot_from_stage_config(
    teams_csv: str | Path,
    config_path: str | Path,
    output_path: str | Path,
) -> None:
    teams = load_teams(teams_csv)
    config = load_stage_config(config_path)
    event_id = str(config["event_id"])
    stage_id = str(config.get("stage_id") or "stage1")
    prediction_cutoff = str(config["prediction_cutoff"])
    feature_window_start = str(config.get("feature_window_start") or prediction_cutoff)
    feature_window_end = str(config.get("feature_window_end") or prediction_cutoff)
    label_window_start = str(config.get("label_window_start") or "")
    label_window_end = str(config.get("label_window_end") or "")
    sample_weight = str(config.get("sample_weight") or "1.0")
    format_type = str(config.get("format_type") or "new_32_team_stage1")
    game_version = str(config.get("game_version") or "CS2")
    round_system = str(config.get("round_system") or "swiss_16_3win_3loss")
    source = str(config.get("vrs_source") or config.get("teams_source") or "")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "event_id",
        "stage_id",
        "team",
        "seed",
        "score",
        "region",
        "prediction_cutoff",
        "feature_window_start",
        "feature_window_end",
        "feature_date",
        "label_window_start",
        "label_window_end",
        "sample_weight",
        "format_type",
        "game_version",
        "round_system",
        "source",
    ]
    with Path(output_path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for team in teams:
            writer.writerow(
                {
                    "event_id": event_id,
                    "stage_id": stage_id,
                    "team": team.name,
                    "seed": team.seed,
                    "score": f"{team.score:.0f}",
                    "region": team.region,
                    "prediction_cutoff": prediction_cutoff,
                    "feature_window_start": feature_window_start,
                    "feature_window_end": feature_window_end,
                    "feature_date": prediction_cutoff,
                    "label_window_start": label_window_start,
                    "label_window_end": label_window_end,
                    "sample_weight": sample_weight,
                    "format_type": format_type,
                    "game_version": game_version,
                    "round_system": round_system,
                    "source": source,
                }
            )


def validate_snapshot(path: str | Path) -> SnapshotValidationResult:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        errors: list[str] = []
        missing = sorted(REQUIRED_SNAPSHOT_COLUMNS - fieldnames)
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
        blocked = sorted(BLOCKED_FEATURE_COLUMNS & fieldnames)
        if blocked:
            errors.append(f"Blocked leakage-prone columns present: {', '.join(blocked)}")

        rows = list(reader)

    for index, row in enumerate(rows, start=2):
        errors.extend(validate_snapshot_row(row, index))

    return SnapshotValidationResult(path=str(path), rows=len(rows), errors=tuple(errors))


def validate_snapshot_row(row: dict[str, str], line_number: int) -> list[str]:
    errors: list[str] = []
    try:
        cutoff = parse_date(row.get("prediction_cutoff", ""))
        feature_start = parse_date(row.get("feature_window_start", ""))
        feature_end = parse_date(row.get("feature_window_end", ""))
        feature_date = parse_date(row.get("feature_date", ""))
    except ValueError as exc:
        return [f"Line {line_number}: {exc}"]

    if feature_start > cutoff:
        errors.append(f"Line {line_number}: feature_window_start is after prediction_cutoff")
    if feature_end > cutoff:
        errors.append(f"Line {line_number}: feature_window_end is after prediction_cutoff")
    if feature_date > cutoff:
        errors.append(f"Line {line_number}: feature_date is after prediction_cutoff")
    if feature_start > feature_end:
        errors.append(f"Line {line_number}: feature_window_start is after feature_window_end")

    sample_weight = row.get("sample_weight", "")
    try:
        if float(sample_weight) <= 0:
            errors.append(f"Line {line_number}: sample_weight must be positive")
    except ValueError:
        errors.append(f"Line {line_number}: sample_weight is not numeric")

    if not row.get("team"):
        errors.append(f"Line {line_number}: team is empty")
    if not row.get("event_id"):
        errors.append(f"Line {line_number}: event_id is empty")
    return errors


def parse_date(value: str) -> date:
    if not value:
        raise ValueError("date value is empty")
    return date.fromisoformat(value)
