"""Transform stage: validated frames -> star-schema dataframes.

Produces dim_date, dim_series, fact_observations (native grain), the wide
monthly mart with derived indicators, and the state-level monthly mart.
"""

import pandas as pd

from etl.config import (
    ALL_SERIES,
    NATIONAL_SERIES,
    PRESSURE_COMPONENTS,
    STATE_SERIES,
    Z_WINDOW_MONTHS,
)


def build_dim_series() -> pd.DataFrame:
    rows = []
    for sid, m in ALL_SERIES.items():
        rows.append({
            "series_id": sid,
            "series_name": m["name"],
            "category": m["category"],
            "frequency": m["frequency"],
            "units": m["units"],
            "geography": m.get("state", "US"),
            "cycle_lens": m["cycle_lens"],
        })
    return pd.DataFrame(rows)


def build_fact_observations(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    parts = []
    for sid, df in frames.items():
        part = df[["obs_date", "value"]].dropna(subset=["value"]).copy()
        part.insert(0, "series_id", sid)
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def build_dim_date(fact: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(fact["obs_date"].min(), fact["obs_date"].max(), freq="D")
    return pd.DataFrame({
        "date_key": dates.strftime("%Y%m%d").astype(int),
        "full_date": dates,
        "year": dates.year,
        "quarter": dates.quarter,
        "month": dates.month,
        "month_name": dates.strftime("%B"),
        "year_month": dates.strftime("%Y-%m"),
    })


def _monthly(series: pd.Series, frequency: str) -> pd.Series:
    """Resample one series to month grain: sub-monthly frequencies average
    within the month, quarterly forward-fills across its months."""
    if frequency in ("D", "W"):
        return series.resample("MS").mean()
    if frequency == "Q":
        return series.resample("MS").ffill()
    return series.resample("MS").last()


def build_mart_monthly(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cols = {}
    for sid, meta in NATIONAL_SERIES.items():
        s = frames[sid].dropna(subset=["value"]).set_index("obs_date")["value"]
        cols[meta["mart_column"]] = _monthly(s, meta["frequency"])
    mart = pd.DataFrame(cols)

    for col in ("consumer_credit", "cpi", "m2", "sp500", "home_price_index"):
        mart[f"{col}_yoy"] = mart[col].pct_change(12) * 100

    for col in PRESSURE_COMPONENTS:
        rolling = mart[col].rolling(Z_WINDOW_MONTHS, min_periods=24)
        mart[f"{col}_z"] = (mart[col] - rolling.mean()) / rolling.std()
    mart["cycle_pressure_score"] = mart[[f"{c}_z" for c in PRESSURE_COMPONENTS]].mean(axis=1)

    mart["yield_inverted"] = mart["yield_spread_10y2y"] < 0
    mart["recession"] = mart["recession"].fillna(0).astype(float) >= 0.5

    mart = mart.reset_index().rename(columns={"index": "month_date", "obs_date": "month_date"})
    mart.insert(0, "year_month", mart["month_date"].dt.strftime("%Y-%m"))
    return mart


def build_mart_state(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    parts = []
    for sid, meta in STATE_SERIES.items():
        df = frames[sid].dropna(subset=["value"])
        parts.append(pd.DataFrame({
            "year_month": df["obs_date"].dt.strftime("%Y-%m"),
            "state": meta["state"],
            "unemployment_rate": df["value"].values,
        }))
    return pd.concat(parts, ignore_index=True)


def run(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    fact = build_fact_observations(frames)
    tables = {
        "dim_series": build_dim_series(),
        "dim_date": build_dim_date(fact),
        "fact_observations": fact,
        "mart_debt_cycle_monthly": build_mart_monthly(frames),
        "mart_state_monthly": build_mart_state(frames),
    }
    for name, df in tables.items():
        print(f"  {name}: {len(df):,} rows")
    return tables
