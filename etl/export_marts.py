"""Export the warehouse tables BI tools consume to CSV, for cloud BI trials
that cannot reach a local Postgres. Files land in data/exports/.

Usage: python -m etl.export_marts
"""

import pandas as pd
import psycopg2

from etl.config import DB, PROJECT_ROOT

EXPORT_DIR = PROJECT_ROOT / "data" / "exports"

TABLES = ["mart_debt_cycle_monthly", "mart_state_monthly", "dim_series", "dim_date"]


def run() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    conn = psycopg2.connect(**DB)
    try:
        for table in TABLES:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            out = EXPORT_DIR / f"{table}.csv"
            df.to_csv(out, index=False)
            print(f"  {out.relative_to(PROJECT_ROOT)}: {len(df):,} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
