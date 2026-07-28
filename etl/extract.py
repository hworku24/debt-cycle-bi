"""Extract stage: pull all configured series from the FRED API into data/raw/fred/."""

import json
import sys

import requests

from etl.config import ALL_SERIES, FRED_API_KEY, FRED_DIR, START_DATE

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_series(series_id: str) -> dict:
    resp = requests.get(
        FRED_URL,
        params={
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": START_DATE,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def run() -> None:
    if not FRED_API_KEY:
        sys.exit("FRED_API_KEY is not set in .env (free key: fred.stlouisfed.org/docs/api/api_key.html)")

    FRED_DIR.mkdir(parents=True, exist_ok=True)
    failed = []
    for series_id, meta in ALL_SERIES.items():
        try:
            payload = fetch_series(series_id)
        except requests.HTTPError as exc:
            print(f"  FAILED {series_id} ({meta['name']}): {exc}")
            failed.append(series_id)
            continue
        (FRED_DIR / f"{series_id}.json").write_text(json.dumps(payload))
        n = len(payload.get("observations", []))
        print(f"  {series_id}: {n} observations ({meta['name']})")

    print(f"Extracted {len(ALL_SERIES) - len(failed)}/{len(ALL_SERIES)} series")
    if failed:
        sys.exit(f"Extraction failed for: {failed}")


if __name__ == "__main__":
    run()
