# Build Notes

This file records the main implementation decisions, problems found during development, and work that is still open. Routine setup steps are covered in the README.

## Pipeline issues found

The first end-to-end run with live FRED data exposed several issues that had not appeared with test data.

### NumPy values and PostgreSQL

Some transformed values were NumPy scalar types, which `psycopg2` could not insert directly. These values are converted to standard Python types before loading.

### `TOTALSL` units

The `TOTALSL` consumer credit series is reported in millions of dollars. The original transformation treated it as billions, which produced incorrect values. The unit conversion was corrected in the transformation layer.

### Leading gaps in `TDSP`

The household debt service ratio series does not contain observations before 2005. These leading gaps are expected and are excluded from the missing-period validation check.

The continuity check still flags missing observations that appear between valid dates.

### Different release schedules

Not every series should be validated using the same frequency and staleness rules.

The validation configuration now accounts for:

* Daily market series that are aggregated to monthly values
* Quarterly series that remain unchanged between releases
* Series with a longer publication delay, such as the Case-Shiller home price index
* Short-history series that begin later than the rest of the dataset

### Series and metric expansion

The first version of the pipeline did not include enough market-price indicators. The following series were added:

* `A191RL1Q225SBEA` for real GDP growth
* `SP500`
* `CSUSHPINSA` for home prices
* `DGS10` for the 10-year Treasury rate
* `DTWEXBGS` for the broad U.S. dollar index

The monthly mart was also expanded with year-over-year measures for home prices and the S&P 500.

A `cycle_lens` field was added to `dim_series` so each indicator can be grouped as:

* `deflationary`
* `inflationary`
* `both`

## Dashboard implementation notes

Both dashboards use the published extracts in `data/exports/` instead of connecting directly to the local PostgreSQL database.

This keeps the builds reproducible and allows the same data files to be used in Qlik Sense and TIBCO Spotfire.

The dashboards follow the same three-page specification:

1. Current Conditions
2. Debt Cycle View
3. State Drill-Down

Some calculations were implemented in the BI tools, but latest-value and period-change logic would be more reliable if calculated directly in PostgreSQL.

Future versions should move the following fields into the warehouse:

```text
latest_value
latest_observation_date
previous_month_value
previous_year_value
month_over_month_change
year_over_year_change
is_latest_observation
```

## Platform-specific problems

### Qlik Sense

Qlik automatically associated the monthly marts and calendar through the shared `year_month` field. This reduced the amount of manual data-model configuration.

CSV files created through pandas represented SQL nulls as empty strings. Qlik loaded those values as text rather than nulls, which affected latest-value expressions.

The load script now includes:

```qlik
SET NullInterpret = '';
```

KPI expressions using `FirstSortedValue` also produced ties because each national month was associated with multiple state rows. Adding `DISTINCT` resolved the issue.

Dates loaded from CSV remained text values and required parsing through functions such as `Date#()` and `MaxString()`.

The application was scaffolded using Qlik's Engine JSON-RPC API and REST APIs. Engine-created objects required more default properties than expected because the standard editor normally adds those values automatically.

Qlik did not provide a simple native option for recession shading on the line charts. The state choropleth was also replaced with a sorted bar chart.

### TIBCO Spotfire

Spotfire kept each imported file as a separate data table. Every visualization therefore needed to reference the correct table explicitly.

New visualizations sometimes inherited the previously active table, which could produce a valid chart using the wrong columns.

Spotfire also defaulted numeric measures to `Sum`. This was incorrect for monthly percentages, rates, and ratios, so affected visualizations had to be changed to `Avg`.

Date fields were grouped by year automatically. The raw monthly date field had to be selected to display the full time series.

Spotfire performed better than Qlik when several measures with different ranges were placed on the same line chart. Its individual-scale option made the multi-measure cycle view easier to read.

The state choropleth and recession shading were not included in the Spotfire version. The state view uses a sorted bar chart instead.

## Remaining work

### Replace `HDTGPDUSQ163N`

The validation pipeline flagged `HDTGPDUSQ163N` as stale. The IMF-sourced household-debt-to-GDP series appears to have stopped updating.

Possible replacements include:

* BIS household credit series `QUSPAM770A`
* A calculated household-debt-to-GDP ratio using Federal Reserve Z.1 data

The replacement should be evaluated before the household debt ratio is treated as a current signal.

### Move dashboard calculations upstream

Latest values, 12-month changes, state rankings, and comparisons with national values should be calculated in the warehouse rather than separately in each BI platform.

A dedicated state table could contain:

```text
state
latest_month
unemployment_rate
national_unemployment_rate
difference_from_national
state_rank
```

This would keep the Qlik and Spotfire dashboards consistent and reduce platform-specific expressions.

### Add recession-period data

The warehouse should include NBER recession start and end dates.

The monthly mart could also include an `is_recession` field so both dashboard platforms can display recession periods without relying on native chart shading.

### Validate dashboard exports

The pipeline currently validates the source data and warehouse tables. Additional checks should be added for the files written to `data/exports/`.

These checks should confirm that:

* All expected columns are present
* Each national KPI has a latest value
* Every state and Washington, D.C. are included
* Exported values match the warehouse
* Row counts do not change unexpectedly between runs
