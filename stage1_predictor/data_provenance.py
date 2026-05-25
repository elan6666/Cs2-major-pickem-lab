from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .hltv_data import is_cloudflare_challenge


@dataclass(frozen=True)
class ProvenanceResult:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()


def validate_fetch_attempt_report(path: str | Path, require_success: bool = True) -> ProvenanceResult:
    errors: list[str] = []
    warnings: list[str] = []
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    attempts = payload.get("attempts", [])
    if not attempts:
        errors.append(f"{path}: no fetch attempts recorded")
    for index, attempt in enumerate(attempts, start=1):
        url = str(attempt.get("url", ""))
        status_code = int(attempt.get("status_code", 0))
        blocked = bool(attempt.get("blocked", False))
        raw_path = Path(str(attempt.get("path", "")))
        if not is_hltv_url(url):
            errors.append(f"{path}: attempt {index} is not an HLTV URL: {url}")
        if require_success and (blocked or status_code != 200):
            errors.append(f"{path}: attempt {index} did not fetch successfully: status={status_code}, blocked={blocked}, url={url}")
        if not raw_path.exists():
            errors.append(f"{path}: attempt {index} raw path does not exist: {raw_path}")
            continue
        raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        if is_cloudflare_challenge(raw_text):
            errors.append(f"{path}: attempt {index} raw path is a Cloudflare challenge page: {raw_path}")
        if status_code != 200:
            warnings.append(f"{path}: attempt {index} status is {status_code}")
    return ProvenanceResult(ok=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_source_csv(
    path: str | Path,
    required_source_fields: tuple[str, ...] = ("source_url",),
    allowed_sources: tuple[str, ...] = ("hltv",),
) -> ProvenanceResult:
    errors: list[str] = []
    row_count = 0
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing_fields = sorted(set(required_source_fields) - fields)
        if missing_fields:
            errors.append(f"{path}: missing source fields: {', '.join(missing_fields)}")
        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            for field in required_source_fields:
                source = row.get(field, "").strip()
                if not source:
                    errors.append(f"{path}:{row_number}: empty {field}")
                elif field in {"source", "source_url"} and not is_allowed_source_url(source, allowed_sources):
                    if allowed_sources == ("hltv",):
                        errors.append(f"{path}:{row_number}: {field} is not an HLTV URL: {source}")
                    else:
                        errors.append(f"{path}:{row_number}: {field} is not an allowed source URL ({', '.join(allowed_sources)}): {source}")
    if row_count == 0:
        errors.append(f"{path}: no data rows")
    return ProvenanceResult(ok=not errors, errors=tuple(errors))


def validate_pretrain_csv(path: str | Path) -> ProvenanceResult:
    required = ("source_url", "cache_path")
    base = validate_source_csv(path, required, allowed_sources=("hltv", "bo3"))
    errors = list(base.errors)
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            cache_path = row.get("cache_path", "").strip()
            if cache_path and not Path(cache_path).exists():
                errors.append(f"{path}:{row_number}: cache_path does not exist: {cache_path}")
    return ProvenanceResult(ok=not errors, errors=tuple(errors), warnings=base.warnings)


def is_hltv_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and parsed.netloc.lower().endswith("hltv.org")


def is_bo3_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and parsed.netloc.lower().endswith("bo3.gg")


def is_allowed_source_url(value: str, allowed_sources: tuple[str, ...]) -> bool:
    for source in allowed_sources:
        if source == "hltv" and is_hltv_url(value):
            return True
        if source == "bo3" and is_bo3_url(value):
            return True
    return False


def combine_results(results: list[ProvenanceResult]) -> ProvenanceResult:
    errors: list[str] = []
    warnings: list[str] = []
    for result in results:
        errors.extend(result.errors)
        warnings.extend(result.warnings)
    return ProvenanceResult(ok=not errors, errors=tuple(errors), warnings=tuple(warnings))
