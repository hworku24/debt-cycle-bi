"""Load stage: create the schema, bulk-insert the star-schema tables, and run
post-load reconciliation checks (row counts and orphaned foreign keys)."""

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from etl.config import DB, SCHEMA_SQL

MART_COLUMNS = [
    "year_month", "month_date", "household_debt_gdp", "federal_debt_gdp",
    "debt_service_ratio", "cc_delinquency", "mortgage_delinquency",
    "consumer_credit", "consumer_credit_yoy", "fedfunds", "mortgage_rate_30y",
    "yield_spread_10y2y", "yield_inverted", "cpi", "cpi_yoy", "m2", "m2_yoy",
    "unemployment", "consumer_sentiment", "recession", "gdp_growth", "sp500",
    "sp500_yoy", "home_price_index", "home_price_index_yoy", "treasury_10y",
    "dollar_index", "household_debt_gdp_z", "debt_service_ratio_z",
    "cc_delinquency_z", "fedfunds_z", "cycle_pressure_score",
]

LOAD_ORDER = {
    "dim_date": ["date_key", "full_date", "year", "quarter", "month", "month_name", "year_month"],
    "dim_series": ["series_id", "series_name", "category", "frequency", "units", "geography", "cycle_lens"],
    "fact_observations": ["series_id", "obs_date", "value"],
    "mart_debt_cycle_monthly": MART_COLUMNS,
    "mart_state_monthly": ["year_month", "state", "unemployment_rate"],
}


def insert_frame(cur, table: str, df: pd.DataFrame, columns: list[str]) -> None:
    clean = df[columns].replace({np.nan: None, pd.NaT: None})
    execute_values(
        cur,
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s",
        clean.itertuples(index=False, name=None),
        page_size=5000,
    )


def post_load_checks(cur, tables: dict[str, pd.DataFrame]) -> None:
    for name, df in tables.items():
        cur.execute(f"SELECT COUNT(*) FROM {name}")
        loaded = cur.fetchone()[0]
        if loaded != len(df):
            raise SystemExit(f"Reconciliation failed: {name} has {loaded} rows, expected {len(df)}")

    cur.execute("""
        SELECT COUNT(*) FROM fact_observations f
        LEFT JOIN dim_series s ON s.series_id = f.series_id
        WHERE s.series_id IS NULL
    """)
    orphans = cur.fetchone()[0]
    if orphans:
        raise SystemExit(f"Reconciliation failed: {orphans} fact rows with no dim_series match")
    print("  post-load reconciliation passed")


def run(tables: dict[str, pd.DataFrame]) -> None:
    conn = psycopg2.connect(**DB)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(SCHEMA_SQL.read_text())
            for name, columns in LOAD_ORDER.items():
                insert_frame(cur, name, tables[name], columns)
                print(f"  loaded {name}")
            post_load_checks(cur, tables)
    finally:
        conn.close()
