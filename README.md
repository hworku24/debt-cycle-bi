# Debt Cycle BI Tracker

A self-refreshing business intelligence pipeline for US debt-cycle and recession-risk analysis. Python ETL ingests 65 national and state-level series from the FRED API, runs an automated data-quality gate, warehouses them in a PostgreSQL star schema, and feeds identical executive dashboards in **Qlik Sense** and **TIBCO Spotfire**. A Claude model on **Amazon Bedrock** turns each month's warehouse metrics into a one-page executive brief, and GitHub Actions refreshes everything monthly.

Architecture inspired by the open-source [debt-cycles-tracker](https://github.com/SimSimButDifferent/debt-cycles-tracker); the warehouse modeling, validation gate, BI layer, and brief generation here are original work.

## Architecture

```
FRED API (14 national + 51 state series)
        |
        v
  etl/extract.py ── raw JSON ──► data/raw/fred/
        |
        v
  etl/validate.py ── data-quality gate ──► reports/validation_report.md
        |     (schema, duplicates, continuity, ranges, staleness)
        v
  etl/transform.py ── star schema + derived indicators
        |     (yoy changes, 10-yr z-scores, yield inversion, cycle pressure score)
        v
  etl/load.py ──► PostgreSQL ──► post-load reconciliation checks
        |                |
        |                ├──► Qlik Sense dashboard      (docs/dashboard-spec.md)
        |                └──► TIBCO Spotfire dashboard  (identical spec)
        v
  etl/brief.py ── Claude on Bedrock ──► reports/briefs/YYYY-MM.md
        |
  GitHub Actions ── monthly cron ── commits refreshed report + brief
```

## How this maps to the BI Engineer role

| Responsibility | Where it lives in this repo |
|---|---|
| Building and managing data pipelines to validate data quality and integrity | `etl/` pipeline with a hard validation gate and post-load reconciliation |
| Supporting data architecture and database management systems | Star schema + derived marts in `sql/schema.sql` |
| Data visualization and reporting with BI tools | Qlik Sense and Spotfire dashboards built to one spec |
| Macroeconomic and microeconomic analysis to inform market development strategies | National debt-cycle indicators + state-level drill-down |
| Stakeholder collaboration to gather requirements | `docs/requirements.md`, a client-style requirements doc the dashboards are built against |
| Data analysis and interpretation to support strategic planning | Derived cycle indicators + the monthly LLM executive brief |
| Continuous process improvement | Scheduled refresh with committed validation reports as an audit trail |

## Quickstart

1. **Configure**
   ```
   cp .env.example .env    # add your FRED API key (free) and DB password
   ```
2. **Start PostgreSQL**
   ```
   docker compose up -d
   ```
3. **Install and run**
   ```
   pip install -r requirements.txt
   python -m etl.run_pipeline
   ```
   The pipeline halts on critical data-quality failures and always writes `reports/validation_report.md`. The Bedrock brief step is optional and skips cleanly without AWS credentials (`--skip-brief` to skip explicitly).
4. **Build the dashboards** by connecting each tool to Postgres and following `docs/dashboard-spec.md`. Free trials:
   - Qlik Sense: https://www.qlik.com/us/trial
   - TIBCO Spotfire: https://www.spotfire.com/trial

## Data-quality gate

Runs before anything touches the warehouse; failures are graded critical (pipeline stops) or warning (logged):

- **Schema enforcement**: every FRED payload has parseable dates and values
- **Key integrity**: no duplicate observation dates per series
- **Continuity**: no missing months mid-series for monthly data
- **Range checks**: values inside plausible bounds per indicator category
- **Staleness detection**: each series updated within its expected release lag
- **Post-load reconciliation**: warehouse row counts match transformed frames, no orphaned foreign keys

## Warehouse

| Table | Grain |
|---|---|
| `fact_observations` | one row per series per native-frequency observation |
| `mart_debt_cycle_monthly` | one row per month, wide: all national indicators + derived yoy, z-scores, yield-inversion flag, composite cycle pressure score |
| `mart_state_monthly` | one row per state per month (unemployment drill-down) |
| `dim_series`, `dim_date` | conformed dimensions |

Derived indicators are computed once in the warehouse so both BI tools show identical numbers.

## Monthly executive brief

`etl/brief.py` sends the last 13 months of mart indicators plus state extremes to Claude on Amazon Bedrock and commits a one-page memo (What Changed, Cycle Position, Regional Notes, What To Watch) to `reports/briefs/`. The pipeline visualizes the data and also writes the first draft of the client memo.

## Scheduled refresh

`.github/workflows/monthly-refresh.yml` runs the full pipeline on the 5th of each month against a containerized Postgres, then commits the refreshed validation report and brief. Repo secrets required: `FRED_API_KEY`, plus optional `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` for the brief.

## Platform comparison

Findings from building the same dashboard in both tools go in [docs/comparison.md](docs/comparison.md); screenshots in `docs/screenshots/` since trial accounts expire and the repo is the durable artifact.
