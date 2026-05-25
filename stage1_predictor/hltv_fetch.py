from __future__ import annotations

import argparse
import json
from pathlib import Path

from .hltv_data import fetch_hltv_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and cache a public HLTV page")
    parser.add_argument("--url", required=True, help="HLTV URL to fetch")
    parser.add_argument("--output", required=True, help="Raw HTML output path")
    parser.add_argument("--status-json", help="Optional fetch status JSON path")
    parser.add_argument("--timeout", type=int, default=30)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = fetch_hltv_page(args.url, args.output, timeout=args.timeout)
    payload = {
        "url": result.url,
        "path": result.path,
        "status_code": result.status_code,
        "blocked": result.blocked,
        "message": result.message,
    }
    if args.status_json:
        Path(args.status_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.status_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 2 if result.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
