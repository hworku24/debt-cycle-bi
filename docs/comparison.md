# Platform Comparison: Qlik Sense vs. TIBCO Spotfire

This comparison is based on building the same three-page debt-cycle dashboard in Qlik Sense and TIBCO Spotfire. Both versions use the requirements in [`docs/dashboard-spec.md`](dashboard-spec.md) and the same CSV extracts from the PostgreSQL warehouse.

Each category is scored from 1 to 5. The goal is not to select one overall winner, but to identify which platform worked better for each part of the project.

## Build notes: Qlik Sense

**Qlik Cloud Analytics trial, built July 30, 2026**

The Qlik Cloud trial could not connect directly to a PostgreSQL database running locally, so the application loads the warehouse extracts stored in `data/exports/`.

This was kept as the permanent setup because it makes the dashboard easier to reproduce without requiring access to the original database.

Qlik automatically associated the following tables through their shared `year_month` field:

* `mart_debt_cycle_monthly`
* `mart_state_monthly`
* Month-level calendar table

No manual joins or table relationships were required.

One issue appeared when loading CSV files created with pandas. SQL null values were written as empty strings, which Qlik interpreted as text rather than null values. This caused expressions using the latest non-null observation to return incorrect results.

The issue was fixed in the load script:

```qlik
SET NullInterpret = '';
```

KPI expressions also required additional handling. Each national month was associated with 51 state rows, which created ties in `FirstSortedValue`. Adding the `DISTINCT` qualifier resolved the problem.

Dates loaded from CSV remained text values, so expressions also required functions such as:

```qlik
Date#()
MaxString()
```

The application was scaffolded through Qlik's Engine JSON-RPC API and REST APIs. These APIs were used to:

* Create the application
* Upload data files
* Update the load script
* Reload the data
* Create sheets
* Create visualizations

Objects created through the Engine API require the full property structure expected by the Qlik client. The standard property panel normally supplies these default values. When they are missing, the visualization renderer can fail even when the main chart definition is valid.

Two parts of the dashboard specification were changed:

* NBER recession shading was not implemented because Qlik line charts do not provide native background bands.
* The state choropleth was replaced with a sorted bar chart.

The bar chart still supports state-level analysis because selecting a state filters the rest of the application through Qlik's associative model.

## Build notes: TIBCO Spotfire

**Spotfire Analyst 15.0 trial, built July 30, 2026**

The Spotfire trial provides Windows desktop software and does not include browser-based authoring.

Because the project was developed from a Mac, Spotfire Analyst was installed on a Windows Server 2022 EC2 instance and accessed through Remote Desktop. Qlik required only a browser.

The trial did not provide an authoring API. Each visualization was created manually in the Spotfire designer. Building the three dashboard pages required roughly 40 interface actions, compared with four main API calls used to scaffold the Qlik application.

Spotfire supports IronPython automation, but it was not available in the trial environment used for this project.

The same CSV extracts were loaded into Spotfire. Unlike Qlik, Spotfire kept each file as a separate data table and did not automatically associate them.

Every visualization has its own data-table setting. New visualizations also inherit the table that was most recently active. This initially caused one chart to use the wrong table and display unrelated columns.

Spotfire uses `Sum` as the default aggregation. This is not appropriate for monthly percentages, rates, and ratios, so each affected axis had to be changed to `Avg`.

For example, summing 12 monthly debt-to-GDP readings could produce a value above 1,200 percent.

Spotfire also grouped the `month_date` field by year automatically. The raw date column had to be selected manually to display the full monthly series.

One clear advantage was support for separate scales within a line chart. The **One scale for each color** option made it possible to display five measures with different ranges without flattening the smaller values.

Spotfire's marking system also supports interaction between visualizations. Selecting a state in one chart filters other visualizations that use the same data table.

Three parts of the dashboard specification were changed:

* NBER recession shading was not implemented.
* The state choropleth was replaced with a sorted bar chart.
* The state chart displays the 1990 to 2026 average for each state instead of the latest monthly value.

The last change was made because creating a reliable latest-value expression through the Spotfire interface required more work than the chart justified.

## What the free tiers do and do not include (30 days)

Both dashboards were built using 30-day trials, so this comparison focuses only on the features used while building the same three-page dashboard.

| Constraint            | Qlik Cloud Analytics trial                             | Spotfire Analyst trial                                |
| --------------------- | ------------------------------------------------------ | ----------------------------------------------------- |
| Authoring environment | Full browser-based authoring                           | Windows desktop application with no browser authoring |
| Data source           | Loaded the published CSV extracts from `data/exports/` | Loaded the same published CSV extracts                |
| Data modeling         | Automatically associated tables through `year_month`   | Kept each file as a separate data table               |
| Automation            | Engine JSON-RPC and REST APIs were available and used  | No authoring API was available in the trial           |
| Sharing               | Cloud application accessible through a browser         | Desktop analysis file                                 |

The scores below compare the platforms as authoring environments for one analyst working from the same data and dashboard specification.

## Setup and connectivity

Scores are from 1 to 5 and are based on building the same dashboard in both tools.

| Dimension                           | Qlik | Spotfire | Notes                                                                                                                                                                                   |
| ----------------------------------- | ---: | -------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Getting to a working environment    |    5 |        2 | Qlik required a browser signup and was ready within minutes. Spotfire required a Windows installation and an EC2 environment because the project was developed from a Mac.              |
| Loading the warehouse extracts      |    4 |        4 | Both tools loaded the same CSV files without major problems.                                                                                                                            |
| Data model and association handling |    5 |        2 | Qlik automatically associated the marts and calendar through `year_month`. Spotfire kept each file separate and required the correct data table to be selected for every visualization. |
| Load performance                    |    4 |        4 | Performance was similar at approximately 36,000 rows. The dataset was too small to show a meaningful difference between the engines.                                                    |

### Setup winner: Qlik Sense

Qlik was easier to access and required less environment setup. Its automatic table associations also reduced the amount of configuration needed after loading the data.

## Dashboard build

| Dimension                    | Qlik | Spotfire | Notes                                                                                                                                                                   |
| ---------------------------- | ---: | -------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| KPI tiles                    |    4 |        4 | Qlik required set-analysis expressions for latest-value logic. Spotfire included sparklines but required each aggregation to be changed from `Sum` to `Avg`.            |
| Time-series charts           |    3 |        4 | Spotfire's individual scales made charts with several differently sized measures easier to read. Qlik kept the measures on one scale.                                   |
| Mixed-magnitude readability  |    2 |        5 | Spotfire clearly performed better when measures had very different ranges.                                                                                              |
| Cross-filtering              |    5 |        4 | Qlik selections applied across the associated model without additional setup. Spotfire marking worked well but was limited to visualizations using the same data table. |
| Specification fidelity       |    3 |        3 | Both versions omitted recession shading and replaced the choropleth with a sorted bar chart.                                                                            |
| Automation and repeatability |    5 |        1 | Qlik allowed the application structure, visualizations, data files, load script, and reload process to be created through APIs. Spotfire required manual authoring.     |

### Visualization winner: Spotfire

Spotfire was stronger for multi-measure time-series charts, especially when the measures had different units or ranges.

### Automation winner: Qlik Sense

Qlik was much stronger when the dashboard needed to be rebuilt or recreated from a script.

## Analyst experience

| Dimension                   | Qlik | Spotfire | Notes                                                                                                                                                    |
| --------------------------- | ---: | -------: | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Time to first working chart |    3 |        4 | Spotfire's property panel was easier to understand at the beginning. Qlik required more familiarity with expressions and set analysis.                   |
| Expression language         |    4 |        3 | Qlik set analysis supported more advanced filtering and latest-value logic. Spotfire's aggregation and `OVER` syntax was simpler for basic calculations. |
| Default behavior            |    4 |        2 | Spotfire's default `Sum` aggregation and year-level date grouping produced misleading results for monthly rate data until changed manually.              |
| Sharing                     |    4 |        3 | Qlik applications are browser-based. Spotfire analysis files remain on the desktop in the tested trial environment.                                      |

### Initial usability winner: Spotfire

Spotfire made it easier to create the first chart and adjust its properties through the interface.

### Dashboard management winner: Qlik Sense

Qlik required more learning at the beginning, but its associative model, browser environment, and APIs made the completed application easier to rebuild and maintain.

## Key differences

### Qlik Sense strengths

* Browser-based authoring
* Automatic associations between tables
* Global selection model
* Strong set-analysis capabilities
* Engine JSON-RPC API
* REST APIs for applications, files, scripts, and reloads
* Reproducible dashboard development
* Browser-based sharing

### Qlik Sense limitations

* Steeper expression-learning curve
* More complicated latest-value KPI logic
* CSV dates required manual parsing
* `FirstSortedValue` required additional handling when associations created duplicate matches
* Limited support for separate scales on multi-measure line charts
* No simple native option for recession shading

### Spotfire strengths

* Easier property panel
* Faster manual creation of basic charts
* Separate scales for each measure
* Strong exploratory workflow
* Useful marking interactions
* Better readability for measures with different ranges
* Built-in KPI sparklines

### Spotfire limitations

* Windows-only desktop authoring in the tested trial
* No browser authoring
* No authoring API available in the trial
* Manual dashboard construction
* Separate data-table selection for each visualization
* New charts can inherit the wrong active table
* `Sum` used as the default aggregation
* Dates grouped by year automatically
* Marking limited by data-table boundaries

## Verdict

### Better for a dashboard other people read: Qlik Sense

Qlik's browser-based environment and global selection model made the application easier to navigate. Users can select an item anywhere in the dashboard and see related data update across the associated model.

### Better for exploring the data: Spotfire

Spotfire made it faster to adjust chart properties and test different combinations of measures. Its support for individual scales was especially useful when comparing rates, ratios, and standardized values in the same visualization.

### Better for a PostgreSQL warehouse project: Qlik Sense

Both trial dashboards used CSV extracts, but Qlik fit the warehouse workflow better because the application could be created and rebuilt programmatically.

The data files, load script, sheets, and visualizations could be recreated from code instead of depending entirely on manual steps.

### Better for a one-time manual investigation: Spotfire

Spotfire would be a strong option when the main task is opening a dataset, testing visualizations, and investigating patterns without needing to reproduce the exact dashboard later.

### Which platform I would use again: Qlik Sense

Qlik is the better fit for the Debt Cycle BI Tracker.

The dashboard follows a fixed specification, refreshes monthly, and needs to remain reproducible. Being able to rebuild the application from a script was more valuable for this project than Spotfire's stronger handling of multi-scale charts.

For a less structured project focused on open-ended exploration, Spotfire would be the better choice.

## Summary

| Category                     | Qlik average | Spotfire average | Winner   |
| ---------------------------- | -----------: | ---------------: | -------- |
| Setup and connectivity       |          4.5 |              3.0 | Qlik     |
| Dashboard build              |          3.7 |              3.5 | Qlik     |
| Analyst experience           |          3.8 |              3.0 | Qlik     |
| Mixed-scale visualization    |          2.0 |              5.0 | Spotfire |
| Automation and repeatability |          5.0 |              1.0 | Qlik     |

The scores reflect this specific dashboard build and the features available in the two trial environments.

## What I would do differently

### Move latest-value calculations into the warehouse

Latest observations, 12-month changes, and previous-period comparisons should be calculated in PostgreSQL instead of separately in each BI tool.

Both platforms made latest-value logic more complicated than the equivalent SQL. Calculating the values upstream would also ensure that both dashboards use the same definitions.

Possible warehouse columns include:

```text
latest_value
latest_observation_date
previous_month_value
previous_year_value
month_over_month_change
year_over_year_change
is_latest_observation
```

### Add recession periods to the data model

The warehouse should include an NBER recession table with one row per recession period:

```text
recession_start
recession_end
recession_name
```

The monthly mart could also include an `is_recession` flag for each month. This would make it easier to show recession periods even when the BI platform does not support native background shading.

### Create a latest-state mart

The state view should use a separate table containing the latest available observation for every state:

```text
mart_state_latest
```

Suggested fields include:

```text
state
latest_month
unemployment_rate
national_unemployment_rate
difference_from_national
state_rank
```

This would remove the need to calculate the latest state value inside either dashboard and would keep the two versions consistent.

### Add checks for the dashboard extracts

The pipeline already validates the warehouse data, but it could also verify the final files written to `data/exports/`.

Useful checks would include:

* Confirming that all expected columns are present
* Confirming that each national KPI has a latest value
* Confirming that all 50 states and Washington, D.C. appear in the state extract
* Comparing exported KPI values with the warehouse values
* Flagging unexpected changes in row counts between monthly runs

These checks would reduce the chance that a successful pipeline run still produces an incomplete dashboard.
