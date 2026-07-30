# Platform Comparison: Qlik Sense vs TIBCO Spotfire

Filled in after both dashboards are built against docs/dashboard-spec.md. Score each dimension 1 to 5 with a short justification; the verdict names a winner per task, not overall.

## Build notes: Qlik Sense (Cloud Analytics trial, built 2026-07-30)

- The cloud trial cannot reach a local Postgres, so the app loads the warehouse extracts published in this repo (data/exports). Kept as the permanent pattern since it makes the dashboard reproducible by anyone.
- Qlik's associative model linked mart_debt_cycle_monthly, mart_state_monthly, and the month-grain calendar automatically through the shared year_month field. Zero join configuration.
- Gotcha: pandas writes SQL NULLs as empty strings and Qlik loads them as empty text values, not nulls. One load-script line fixes it: SET NullInterpret = '';. Without it, "latest non-null value" KPI expressions silently break.
- Gotcha: KPI expressions over the associated model hit FirstSortedValue ties (each month associates to 51 state rows). The DISTINCT qualifier resolves it. Dates loaded from CSV stay text, so Date#()/MaxString() are needed in expressions.
- Beyond the standard editor, the app can be scaffolded programmatically: sheets and charts were created through the Qlik Engine JSON-RPC API (websocket) and the REST APIs (apps, data-files, scripts, reloads). Engine-created charts need the client's full default property tree or the visualization renderer errors; the property panel normally supplies those defaults.
- Spec deviation: NBER recession shading is not implemented; Qlik has no native background band shading on line charts. A combo-chart workaround exists but was skipped for time. Choropleth was swapped for a sorted bar chart plus the selection model, which gives equivalent drill-down interaction.
- Qlik's selection model (click any state, everything filters) came free with the data model, which is the associative engine's real selling point in practice.

## Setup and connectivity

| Dimension | Qlik Sense | Spotfire | Notes |
|---|---|---|---|
| Postgres connection setup | | | |
| Data model / association handling | | | |
| Load performance on fact_observations | | | |

## Dashboard build

| Dimension | Qlik Sense | Spotfire | Notes |
|---|---|---|---|
| KPI tiles (page 1) | | | |
| Recession shading on time series (page 2) | | | |
| Choropleth + cross-filtering (page 3) | | | |
| Spec fidelity (deviations forced) | | | |

## Analyst experience

| Dimension | Qlik Sense | Spotfire | Notes |
|---|---|---|---|
| Learning curve | | | |
| Expression/calculation language | | | |
| Sharing and export | | | |

## Verdict

- Best for executive dashboards:
- Best for exploratory analysis:
- Best for a Postgres-warehouse stack:
- What I would tell a client choosing between them:
