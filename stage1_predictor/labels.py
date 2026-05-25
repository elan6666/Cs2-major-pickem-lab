from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_LABEL_COLUMNS = {
    "event_id",
    "stage_id",
    "team",
    "final_record",
    "advanced",
    "went_3_0",
    "went_0_3",
    "source",
}

VALID_RECORDS = {"3-0", "3-1", "3-2", "2-3", "1-3", "0-3"}
ADVANCED_RECORDS = {"3-0", "3-1", "3-2"}


@dataclass(frozen=True)
class LabelValidationResult:
    path: str
    rows: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def load_label_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_labels(path: str | Path) -> LabelValidationResult:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        errors: list[str] = []
        missing = sorted(REQUIRED_LABEL_COLUMNS - fieldnames)
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
        rows = list(reader)

    errors.extend(validate_label_rows(rows))
    return LabelValidationResult(path=str(path), rows=len(rows), errors=tuple(errors))


def validate_label_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if len(rows) != 16:
        errors.append(f"Stage 1 labels require exactly 16 teams, got {len(rows)}")

    teams = [row.get("team", "").strip() for row in rows]
    if any(not team for team in teams):
        errors.append("Team names cannot be empty")
    if len(set(teams)) != len(teams):
        errors.append("Team names must be unique")

    event_ids = {row.get("event_id", "").strip() for row in rows}
    stage_ids = {row.get("stage_id", "").strip() for row in rows}
    if len(event_ids) != 1 or "" in event_ids:
        errors.append("Labels must contain exactly one non-empty event_id")
    if len(stage_ids) != 1 or "" in stage_ids:
        errors.append("Labels must contain exactly one non-empty stage_id")

    advanced_count = 0
    three_zero_count = 0
    zero_three_count = 0
    for index, row in enumerate(rows, start=2):
        record = row.get("final_record", "").strip()
        if record not in VALID_RECORDS:
            errors.append(f"Line {index}: invalid final_record '{record}'")
            continue

        expected_advanced = record in ADVANCED_RECORDS
        expected_three_zero = record == "3-0"
        expected_zero_three = record == "0-3"

        advanced = parse_bool(row.get("advanced", ""))
        went_3_0 = parse_bool(row.get("went_3_0", ""))
        went_0_3 = parse_bool(row.get("went_0_3", ""))

        if advanced is None:
            errors.append(f"Line {index}: advanced must be true/false")
        elif advanced != expected_advanced:
            errors.append(f"Line {index}: advanced does not match final_record")
        if went_3_0 is None:
            errors.append(f"Line {index}: went_3_0 must be true/false")
        elif went_3_0 != expected_three_zero:
            errors.append(f"Line {index}: went_3_0 does not match final_record")
        if went_0_3 is None:
            errors.append(f"Line {index}: went_0_3 must be true/false")
        elif went_0_3 != expected_zero_three:
            errors.append(f"Line {index}: went_0_3 does not match final_record")

        advanced_count += int(expected_advanced)
        three_zero_count += int(expected_three_zero)
        zero_three_count += int(expected_zero_three)

    if advanced_count != 8:
        errors.append(f"Stage 1 labels require exactly 8 advanced teams, got {advanced_count}")
    if three_zero_count != 2:
        errors.append(f"Stage 1 labels require exactly two 3-0 teams, got {three_zero_count}")
    if zero_three_count != 2:
        errors.append(f"Stage 1 labels require exactly two 0-3 teams, got {zero_three_count}")

    return errors


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None
