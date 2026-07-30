"""Monthly executive brief: reads the latest mart rows from Postgres, asks
Claude (via Amazon Bedrock) for a one-page 'what changed and why it matters'
memo, and writes it to reports/briefs/YYYY-MM.md.

Optional stage: skipped cleanly when AWS credentials are absent, so the core
pipeline works without any AWS setup.
"""

import pandas as pd
import psycopg2

from etl.config import AWS_REGION, BRIEF_MODEL, BRIEFS_DIR, DB

PROMPT = """You are writing a monthly executive brief for a business intelligence \
client tracking US debt-cycle and recession risk. Below are the last 13 months of \
warehouse indicators (most recent last), then the 5 states with the highest and \
lowest current unemployment.

{mart_table}

State unemployment extremes (latest month):
{state_table}

Write a one-page markdown memo titled "Debt Cycle Brief - {latest_month}" with \
sections: What Changed This Month, Cycle Position (reference the z-scores and \
cycle_pressure_score), Regional Notes, and What To Watch Next Month. Ground every \
claim in the numbers provided; do not invent data. Keep it under 500 words, use \
plain punctuation (no em dashes), and write for a non-technical executive audience."""


def fetch_context() -> tuple[pd.DataFrame, pd.DataFrame]:
    conn = psycopg2.connect(**DB)
    try:
        mart = pd.read_sql(
            "SELECT * FROM mart_debt_cycle_monthly ORDER BY year_month DESC LIMIT 13",
            conn,
        ).sort_values("year_month")
        states = pd.read_sql(
            """
            (SELECT state, unemployment_rate FROM mart_state_monthly
             WHERE year_month = (SELECT MAX(year_month) FROM mart_state_monthly)
             ORDER BY unemployment_rate DESC LIMIT 5)
            UNION ALL
            (SELECT state, unemployment_rate FROM mart_state_monthly
             WHERE year_month = (SELECT MAX(year_month) FROM mart_state_monthly)
             ORDER BY unemployment_rate ASC LIMIT 5)
            """,
            conn,
        )
    finally:
        conn.close()
    return mart, states


def run() -> None:
    try:
        from anthropic import AnthropicBedrockMantle
    except ImportError:
        print("  brief skipped: anthropic SDK not installed (pip install 'anthropic[bedrock]')")
        return

    mart, states = fetch_context()
    if mart.empty:
        print("  brief skipped: mart is empty")
        return
    latest_month = mart["year_month"].iloc[-1]

    numeric = mart.drop(columns=["month_date"]).round(2)
    prompt = PROMPT.format(
        mart_table=numeric.to_markdown(index=False),
        state_table=states.round(2).to_markdown(index=False),
        latest_month=latest_month,
    )

    try:
        client = AnthropicBedrockMantle(aws_region=AWS_REGION)
        response = client.messages.create(
            model=BRIEF_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        print(f"  brief skipped: Bedrock call failed ({exc})")
        return

    if response.stop_reason == "refusal":
        print("  brief skipped: model declined the request")
        return

    text = next((b.text for b in response.content if b.type == "text"), "")
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    out = BRIEFS_DIR / f"{latest_month}.md"
    out.write_text(text + "\n")
    print(f"  brief written: reports/briefs/{latest_month}.md")


if __name__ == "__main__":
    run()
