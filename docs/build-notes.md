# Build notes

What I did in what order, and what broke. Mostly here so I remember why things are the way they are.

The BI trials expire after 30 days, so I left both dashboard builds until the pipeline was finished and I could do them back to back.

## Scaffold

Repo structure, ETL modules, schema, planning docs. Committed 2026-07-28.

## First end-to-end run

Get real data flowing on this machine.

- FRED API key into `.env` (free, fred.stlouisfed.org)
- Docker Desktop was already installed; `docker compose up -d`
- `pip install -r requirements.txt`
- `python -m etl.run_pipeline --skip-brief`. First contact with live data surfaced three real issues: numpy scalars need unwrapping before psycopg2 inserts, TOTALSL is reported in millions not billions, and TDSP has no data before 2005 so leading gaps had to be excluded from the missing-value check
- Spot check the marts: data through 2026-07, pressure score 0.67, 51 states, 54,394 fact rows
- Commit the first validation report. Six warnings remain, all staleness: five quarterly series sitting between normal releases, plus HDTGPDUSQ163N which has stopped updating (see backlog)


## Metric expansion

Add the market-price indicators the first pass skipped, plus the cycle categorization.

- New series in config: A191RL1Q225SBEA (real GDP growth), SP500, CSUSHPINSA (Case-Shiller), DGS10, DTWEXBGS (dollar index)
- `cycle_lens` column on dim_series (deflationary / inflationary / both)
- New mart columns, including home price yoy and S&P yoy
- Series counts updated in README, requirements, and the dashboard spec (markets panel added to page 2)
- Short-history and slow-release series: SP500 and the other daily series skip the monthly continuity check by design; Case-Shiller's 2-month release lag got a staleness_days override
- Re-run against live data: sp500_yoy 19.0%, home_price_index_yoy 1.3% in the latest month, cycle_lens populated for all 70 series


## Publish and automate

- Repo name: debt-cycle-bi, public
- Pushed and confirmed the repo renders correctly on GitHub
- FRED_API_KEY repo secret added; workflow went green on the first manual dispatch and committed a refreshed validation report as github-actions[bot]
- AWS set up; first executive brief generated and committed (reports/briefs/2026-07.md). The account only has the classic bedrock-runtime endpoint, so the brief uses a cross-region inference profile (us.anthropic.claude-sonnet-4-5) instead of the newer mantle endpoint ids


## Qlik dashboard

Trial clock started 2026-07-30 (Qlik Cloud Analytics, 30 days).

- Trial started; app "Debt Cycle BI" created in the tenant
- Data loaded from the repo's published extracts (cloud trial cannot reach localhost; see comparison.md build notes)
- Built the three pages: Current Conditions (8 KPIs + pressure trend), Debt Cycle View (4 macro charts), State Drill-Down (sorted bar, state vs national trend, 12-month change table). All verified rendering with live values
- Observations captured in comparison.md while fresh
- Screenshots into docs/screenshots/, prefixed qlik-, cropped to the canvas

## Spotfire dashboard

Same three pages, same spec.

- Trial turned out to be Windows-only desktop software. No Windows machine here, so the build ran on a Windows Server 2022 instance on EC2 (m7i-flex.large, on free credits) over RDP
- Built pages 1 to 3: eight KPI tiles with sparklines, two multi-measure time series, state bar chart with table and trend
- Screenshots prefixed spotfire-, cropped
- Build notes in comparison.md, including the Sum-by-default and Year-binning traps and the individual-scales win

## Comparison writeup

- Every table in comparison.md scored, with the verdict and a "what I would do differently" section
- All six screenshots in the README
- Read-through pass


## Still open

- Replace HDTGPDUSQ163N. The validation gate flagged it 483 days stale on the first live run; the IMF-sourced household debt to GDP series has effectively stopped updating. Candidate replacement: BIS credit-to-households series (QUSPAM770A) or computing the ratio from Z.1 components.
