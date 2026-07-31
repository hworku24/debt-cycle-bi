# Debt Cycle BI Tracker

US federal debt passed 120% of GDP, credit card delinquencies are climbing, and the yield curve spent most of two years inverted. I wanted a way to look at all of that together and ask a specific question every month: where are we in the debt cycle, and is stress building or easing?

The framing I settled on splits debt cycles into two kinds. In a deflationary cycle the debt burden grows because prices and incomes fall while the debt stays fixed. In an inflationary one the currency absorbs the damage instead. Which kind you are in changes which indicators matter, so I tag every series with the cycle it speaks to. Individual charts on FRED did not give me that picture, because the interesting part is how indicators move relative to each other and relative to their own history. So I built a small warehouse that pulls the series, computes the comparisons I actually wanted (year-over-year changes, z-scores against a rolling 10-year window, a composite stress score), and refreshes itself every month.

Python pulls 70 series from the Federal Reserve's FRED API, a validation gate checks them before anything loads, and PostgreSQL holds a star schema with the derived indicators. The same three-page dashboard is built in both Qlik Sense and TIBCO Spotfire, because I wanted to learn both tools and building the same thing twice is the only honest way to compare them. A Claude model on Amazon Bedrock writes a one-page summary of what changed each month.

Architecture inspired by the open-source [debt-cycles-tracker](https://github.com/SimSimButDifferent/debt-cycles-tracker); the warehouse modeling, validation gate, BI layer, and brief generation here are original work.

## What it says right now

Last full read, June 2026 (the quarterly series lag by a quarter, which is why some readings are dated January):

| Indicator | Latest | Read |
|---|---|---|
| Composite pressure score | 0.67 | Stress about two thirds of a standard deviation above the last decade |
| Federal debt to GDP | 122.6% (Jan) | Elevated and still climbing |
| Household debt service ratio | 11.2% (Jan) | Near its long-run average, not a crisis level |
| Credit card delinquency | 2.9% (Jan) | Roughly one standard deviation above normal, up sharply from the 2021 low |
| Fed funds | 3.63% | Easing, well down from the 2023 peak |
| 10y minus 2y spread | +0.36pp | Positive again after the long inversion |
| CPI year over year | 3.23% (Jul) | Still above target |
| Unemployment | 4.2% | Low nationally, but states run from 2.0% to 6.0% |

The short version: household balance sheets are showing strain in delinquencies while rates and the curve have been normalizing. Sovereign debt is the piece that keeps trending the wrong way regardless of where the cycle is.

## Architecture

```
FRED API (19 national + 51 state series)
        |
        v
  etl/extract.py -- raw JSON --> data/raw/fred/
        |
        v
  etl/validate.py -- data-quality gate --> reports/validation_report.md
        |     (schema, duplicates, continuity, ranges, staleness)
        v
  etl/transform.py -- star schema + derived indicators
        |     (yoy changes, 10-yr z-scores, yield inversion, cycle pressure score)
        v
  etl/load.py --> PostgreSQL --> post-load reconciliation checks
        |                |
        |                +--> Qlik Sense dashboard      (docs/dashboard-spec.md)
        |                +--> TIBCO Spotfire dashboard  (identical spec)
        v
  etl/brief.py -- Claude on Bedrock --> reports/briefs/YYYY-MM.md
        |
  GitHub Actions -- monthly cron -- commits refreshed report + brief
```

## Docs

| Document | Contents |
|---|---|
| [Scope](docs/requirements.md) | What the tracker answers, what it deliberately does not, and the questions each dashboard page has to satisfy |
| [Wireframes](docs/wireframes/README.md) | Digital wireframes for the three dashboard pages |
| [User flow](docs/user-flow.md) | How the monthly read and the maintenance loop actually run |
| [Tech stack](docs/tech-stack.md) | Tools, languages, libraries, and the reasoning behind each |
| [File structure](docs/file-structure.md) | Repository layout and conventions |
| [Dashboard spec](docs/dashboard-spec.md) | The page-by-page spec both BI tools implement |

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

Derived indicators are computed once in the warehouse so both BI tools show identical numbers. Each series in `dim_series` carries a `cycle_lens` tag (deflationary, inflationary, or both) so dashboards can group indicators by which kind of debt cycle they speak to.

## Monthly written summary

`etl/brief.py` sends the last 13 months of mart indicators plus state extremes to Claude on Amazon Bedrock and commits a one-page memo (What Changed, Cycle Position, Regional Notes, What To Watch) to `reports/briefs/`. It saves me writing the same monthly summary by hand, and it forces the numbers to be stated in plain language rather than left as charts.

## Scheduled refresh

`.github/workflows/monthly-refresh.yml` runs the full pipeline on the 5th of each month against a containerized Postgres, then commits the refreshed validation report and brief. Repo secrets required: `FRED_API_KEY`, plus optional `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` for the brief.

## Dashboards

The same three-page spec built twice. Findings from building it in both tools are in [docs/comparison.md](docs/comparison.md).

**Qlik Sense**

![Qlik current conditions](docs/screenshots/qlik-current-conditions.png)
![Qlik debt cycle view](docs/screenshots/qlik-debt-cycle-view.png)
![Qlik state drill-down](docs/screenshots/qlik-state-drilldown.png)

**TIBCO Spotfire**

![Spotfire current conditions](docs/screenshots/spotfire-current-conditions.png)
![Spotfire debt cycle view](docs/screenshots/spotfire-debt-cycle-view.png)
![Spotfire state drill-down](docs/screenshots/spotfire-state-drilldown.png)

## Platform comparison

Scored tables and the verdict are in [docs/comparison.md](docs/comparison.md). Short version: Qlik for governed, reproducible dashboards (the entire app was built through its Engine and REST APIs); Spotfire for exploratory analysis (individual scales per measure made a five-measure chart readable that Qlik flattened).
