"""Data-quality gate. Runs on the raw FRED payloads before anything touches the
warehouse; writes reports/validation_report.md every run.

Checks: payload schema, duplicate observation dates, missing-value density,
monthly continuity (no gaps mid-series), plausible value ranges, and staleness
(series not updated within its expected release lag). Critical issues stop the
pipeline; warnings are recorded and the run continues.
"""

import json
from dataclasses import dataclass

import pandas as pd

from etl.config import ALL_SERIES, FRED_DIR, RANGE_BOUNDS, REPORTS_DIR, STALENESS_DAYS


@dataclass
class Issue:
    severity: str  # "critical" | "warning"
    series_id: str
    check: str
    detail: str


def load_series(series_id: str) -> pd.DataFrame:
    """Parse one raw FRED payload into a (obs_date, value) frame. FRED encodes
    missing values as '.', which becomes NaN here."""
    payload = json.loads((FRED_DIR / f"{series_id}.json").read_text())
    obs = payload.get("observations", [])
    df = pd.DataFrame(obs)
    if not df.empty:
        df["obs_date"] = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def check_series(series_id: str, df: pd.DataFrame) -> list[Issue]:
    meta = ALL_SERIES[series_id]
    issues = []

    if df.empty or "date" not in df.columns or "value" not in df.columns:
        return [Issue("critical", series_id, "schema", "payload missing observations/date/value")]
    if df["obs_date"].isna().any():
        return [Issue("critical", series_id, "date_parse", "unparseable observation dates")]

    dupes = int(df.duplicated(subset=["obs_date"]).sum())
    if dupes:
        issues.append(Issue("critical", series_id, "duplicate_dates", f"{dupes} duplicate observation dates"))

    # Ignore leading missing values: FRED pads with '.' before a series'
    # actual start (e.g. TDSP begins in 2005 but the request starts at 1990).
    vals = df["value"]
    first_valid = vals.first_valid_index()
    missing_pct = 100.0 if first_valid is None else vals.loc[first_valid:].isna().mean() * 100
    if missing_pct > 10:
        issues.append(Issue("warning", series_id, "missing_values", f"{missing_pct:.1f}% missing after series start"))

    if meta["frequency"] == "M":
        months = df["obs_date"].dt.to_period("M").drop_duplicates()
        expected = pd.period_range(months.min(), months.max(), freq="M")
        gaps = len(expected) - len(months)
        if gaps:
            issues.append(Issue("warning", series_id, "continuity", f"{gaps} missing months mid-series"))

    lo, hi = meta.get("bounds", RANGE_BOUNDS[meta["category"]])
    out_of_range = int((~df["value"].dropna().between(lo, hi)).sum())
    if out_of_range:
        issues.append(Issue("warning", series_id, "range", f"{out_of_range} values outside [{lo}, {hi}]"))

    max_lag = meta.get("staleness_days", STALENESS_DAYS[meta["frequency"]])
    age_days = (pd.Timestamp.now() - df["obs_date"].max()).days
    if age_days > max_lag:
        issues.append(Issue("warning", series_id, "staleness", f"latest observation is {age_days} days old (limit {max_lag})"))

    return issues


def write_report(frames: dict[str, pd.DataFrame], issues: list[Issue]) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    total_obs = sum(len(df) for df in frames.values())
    lines = [
        "# Data Quality Validation Report",
        "",
        f"Series checked: {len(frames)} | Total observations: {total_obs:,}",
        "",
        "## Issues",
        "",
    ]
    if not issues:
        lines.append("All checks passed.")
    else:
        lines.append("| Severity | Series | Check | Detail |")
        lines.append("|---|---|---|---|")
        for i in sorted(issues, key=lambda x: (x.severity, x.series_id)):
            lines.append(f"| {i.severity} | {i.series_id} | {i.check} | {i.detail} |")
    (REPORTS_DIR / "validation_report.md").write_text("\n".join(lines) + "\n")


def run() -> dict[str, pd.DataFrame]:
    """Load and validate every raw series. Raises on critical issues; returns
    parsed frames keyed by series id so transform doesn't re-parse."""
    frames, issues = {}, []
    for series_id in ALL_SERIES:
        df = load_series(series_id)
        frames[series_id] = df
        issues += check_series(series_id, df)

    write_report(frames, issues)

    criticals = [i for i in issues if i.severity == "critical"]
    warnings = [i for i in issues if i.severity == "warning"]
    print(f"Validation: {len(criticals)} critical, {len(warnings)} warnings "
          f"(report: reports/validation_report.md)")
    if criticals:
        for i in criticals:
            print(f"  CRITICAL [{i.series_id}] {i.check}: {i.detail}")
        raise SystemExit("Critical data-quality failures, pipeline stopped.")
    return frames


if __name__ == "__main__":
    run()
