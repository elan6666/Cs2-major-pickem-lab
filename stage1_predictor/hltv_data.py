from __future__ import annotations

import csv
import html
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


@dataclass(frozen=True)
class FetchResult:
    url: str
    path: str
    status_code: int
    blocked: bool
    message: str


@dataclass(frozen=True)
class HltvTeamMetric:
    team: str
    maps: int
    kd_diff: int | None
    kd: float | None
    rating: float
    source_type: str = "team_stats"
    source_url: str = ""


def fetch_hltv_page(
    url: str,
    output_path: str | Path,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = 30,
) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            status_code = int(response.status)
    except HTTPError as exc:
        body = exc.read()
        status_code = int(exc.code)
    except URLError as exc:
        return FetchResult(url=url, path=str(path), status_code=0, blocked=False, message=str(exc.reason))

    text = body.decode("utf-8", errors="replace")
    path.write_text(text, encoding="utf-8")
    blocked = is_cloudflare_challenge(text) or status_code in {403, 429}
    message = "blocked by challenge" if blocked else "ok"
    return FetchResult(url=url, path=str(path), status_code=status_code, blocked=blocked, message=message)


def is_cloudflare_challenge(text: str) -> bool:
    lowered = text.lower()
    return "cf-mitigated" in lowered or "just a moment" in lowered or "challenge-platform" in lowered


def load_hltv_team_metrics(path: str | Path, team_names: list[str] | None = None) -> dict[str, HltvTeamMetric]:
    source = Path(path).read_text(encoding="utf-8")
    if looks_like_metric_csv(source):
        return load_metric_csv(path)
    return parse_hltv_team_stats(source, team_names)


def looks_like_metric_csv(source: str) -> bool:
    first_line = source.splitlines()[0] if source.splitlines() else ""
    normalized = first_line.lower().replace(" ", "")
    return normalized.startswith("team,") and ("rating3" in normalized or "rating" in normalized)


def load_metric_csv(path: str | Path) -> dict[str, HltvTeamMetric]:
    metrics: dict[str, HltvTeamMetric] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            team = row.get("team", "").strip()
            if not team:
                continue
            rating = parse_optional_float(row.get("rating3") or row.get("rating"))
            maps = parse_optional_int(row.get("maps"))
            if rating is None or maps is None:
                continue
            metrics[team] = HltvTeamMetric(
                team=team,
                maps=maps,
                kd_diff=parse_optional_int(row.get("kd_diff")),
                kd=parse_optional_float(row.get("kd")),
                rating=rating,
                source_type=row.get("source_type", "team_stats").strip() or "team_stats",
                source_url=row.get("source_url", "").strip(),
            )
    return metrics


def parse_hltv_team_stats(source: str, team_names: list[str] | None = None) -> dict[str, HltvTeamMetric]:
    normalized = normalize_hltv_table_text(source)
    metrics: dict[str, HltvTeamMetric] = {}
    names = sorted(team_names or [], key=len, reverse=True)
    for line in normalized.splitlines():
        row = parse_hltv_team_stats_line(line, names)
        if row:
            metrics[row.team] = row
    return metrics


def parse_hltv_team_overview_current_roster(source: str, team: str) -> HltvTeamMetric | None:
    normalized = normalize_hltv_table_text(source)
    section = extract_current_roster_section(normalized)
    if not section:
        return None

    rows = parse_compact_roster_rows(section)
    if not rows:
        rows = parse_line_split_roster_rows(section)
    if not rows:
        return None

    maps = round(sum(row[0] for row in rows) / len(rows))
    rating = sum(row[1] for row in rows) / len(rows)
    return HltvTeamMetric(
        team=team,
        maps=maps,
        kd_diff=None,
        kd=None,
        rating=rating,
        source_type="team_overview_current_roster",
    )


def extract_current_roster_section(normalized: str) -> str:
    header = "Player Status Time on team Maps played Rating 3.0"
    start = normalized.find(header)
    if start < 0:
        return ""
    tail = normalized[start + len(header) :]
    end_markers = ["* Will only show", "## Roster timeline", "Roster timeline"]
    end_positions = [tail.find(marker) for marker in end_markers if tail.find(marker) >= 0]
    end = min(end_positions) if end_positions else len(tail)
    return tail[:end]


def parse_compact_roster_rows(section: str) -> list[tuple[int, float]]:
    rows: list[tuple[int, float]] = []
    for match in re.finditer(r"STARTER(?P<body>.*?)(?=STARTER|$)", section, flags=re.DOTALL):
        numbers = re.findall(r"\d+(?:\.\d+)?", match.group("body"))
        row = parse_roster_numbers(numbers)
        if row:
            rows.append(row)
    return rows


def parse_line_split_roster_rows(section: str) -> list[tuple[int, float]]:
    rows: list[tuple[int, float]] = []
    lines = [line.strip(" |") for line in section.splitlines() if line.strip(" |")]
    for index, line in enumerate(lines):
        if line != "STARTER":
            continue
        window = " ".join(lines[index + 1 : index + 8])
        numbers = re.findall(r"\d+(?:\.\d+)?", window)
        row = parse_roster_numbers(numbers)
        if row:
            rows.append(row)
    return rows


def parse_roster_numbers(numbers: list[str]) -> tuple[int, float] | None:
    if len(numbers) < 2:
        return None
    for index in range(len(numbers) - 1):
        maps_text = numbers[index]
        rating_text = numbers[index + 1]
        if "." not in rating_text:
            continue
        maps = int(float(maps_text))
        rating = float(rating_text)
        if maps >= 1 and 0.5 <= rating <= 2.0:
            return maps, rating
    return None


def normalize_hltv_table_text(source: str) -> str:
    text = html.unescape(source).replace("\xa0", " ")
    if "<" in text and ">" in text:
        text = re.sub(r"(?i)</t[dh]>", " | ", text)
        text = re.sub(r"(?i)</tr>", "\n", text)
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return "\n".join(line.strip(" |") for line in text.splitlines())


def parse_hltv_team_stats_line(line: str, team_names: list[str]) -> HltvTeamMetric | None:
    if not line or "Team Maps" in line or "Rating" in line and "Maps" in line:
        return None
    if team_names:
        lowered = line.lower()
        for team in team_names:
            index = lowered.find(team.lower())
            if index < 0:
                continue
            tail = line[index + len(team) :]
            numbers = re.findall(r"[+-]?\d+(?:\.\d+)?", tail)
            if len(numbers) < 4:
                continue
            return HltvTeamMetric(
                team=team,
                maps=int(float(numbers[0])),
                kd_diff=int(float(numbers[1])),
                kd=float(numbers[2]),
                rating=float(numbers[3]),
            )

    match = re.search(
        r"(?P<team>[A-Za-z0-9 ._'&-]+?)\s+(?P<maps>\d+)\s+"
        r"(?P<kd_diff>[+-]?\d+)\s+(?P<kd>\d+(?:\.\d+)?)\s+"
        r"(?P<rating>\d+(?:\.\d+)?)$",
        line,
    )
    if not match:
        return None
    team = re.sub(r"^Image:\s*[A-Za-z ]+", "", match.group("team")).strip()
    if not team:
        return None
    return HltvTeamMetric(
        team=team,
        maps=int(match.group("maps")),
        kd_diff=int(match.group("kd_diff")),
        kd=float(match.group("kd")),
        rating=float(match.group("rating")),
    )


def parse_optional_int(value: str | None) -> int | None:
    if value is None or value.strip() in {"", "-"}:
        return None
    return int(float(value.strip().replace("+", "")))


def parse_optional_float(value: str | None) -> float | None:
    if value is None or value.strip() in {"", "-"}:
        return None
    return float(value.strip())
