# Dashboard Specification

Both tools (Qlik Sense, TIBCO Spotfire) implement this spec identically, reading the same Postgres marts. Deviations forced by a tool's limitations are recorded in comparison.md.

**Data sources:** `mart_debt_cycle_monthly` (one row per month), `mart_state_monthly` (one row per state per month), `dim_date` for calendar filtering.

## Page 1: Current Conditions (executive KPI view)

KPI tiles, latest month vs 12 months ago:
- Cycle pressure score (with trend arrow)
- Household debt to GDP
- Debt service ratio
- Credit card delinquency
- Fed funds rate
- Unemployment
- CPI year-over-year
- Yield curve status (inverted yes/no, spread value)

Below the tiles: 24-month sparkline strip for each KPI.

## Page 2: Debt Cycle View (macro)

- Main chart: household debt to GDP and federal debt to GDP, 1990 to present, NBER recessions shaded (`recession` column).
- Secondary chart: cycle pressure score with its four component z-scores, same period, recessions shaded.
- Credit conditions panel: consumer credit yoy, delinquency rates, mortgage rate.
- Money and prices panel: CPI yoy, M2 yoy, fed funds.
- Markets panel: S&P 500 yoy, home price yoy, 10Y Treasury yield, dollar index.
- Where the tool makes it easy, offer a filter on `dim_series.cycle_lens` to view deflationary vs inflationary indicators separately.

## Page 3: State Drill-Down (micro)

- Choropleth map of state unemployment, latest month.
- Selecting a state filters a trend chart: that state vs national unemployment.
- Table: top and bottom 10 states with 12-month change.

## Conventions

- All derived numbers come from the warehouse; no calculated measures in the BI layer beyond simple deltas.
- Latest month labeled explicitly on every page.
- Screenshots of each page in both tools go to docs/screenshots/ (trials expire; the repo is the durable artifact).
