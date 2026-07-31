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

## Build notes: TIBCO Spotfire (Analyst 15.0 trial, built 2026-07-30)

- The trial ships Windows-only desktop software (Spotfire Analyst installer); there is no browser authoring in the trial tier. Built on a Windows Server 2022 instance on EC2 (m7i-flex.large), accessed over RDP from a Mac. Qlik needed nothing but a browser.
- No authoring API. Every visualization was created by hand in the designer: roughly 40 UI actions against Qlik's 4 API calls for the same three pages. Spotfire has an IronPython automation layer, but it is not exposed in the trial.
- Loaded the same repo CSV extracts. Spotfire keeps each file as a separate data table and does not auto-associate them: every visualization has an explicit Data table selector, and new charts inherit whichever table was last active, which silently produced a chart with the wrong columns until corrected. Qlik's associative engine linked the same files on year_month with no configuration.
- Aggregation defaults to Sum. Monthly rates and ratios have to be switched to Avg on every axis or the values are meaningless (a debt-to-GDP ratio summed across 12 months reads 1200).
- Date handling: month_date binned to Year by default, which flattened 36 years into a handful of points. The raw column has to be picked explicitly from the axis menu.
- Individual scales are supported on line charts ("One scale for each color"), which made the five-measure cycle chart readable. This is the one place Spotfire clearly beat the Qlik build, where the same chart had to stay on a single scale.
- Marking (click a bar, other visualizations filter) works across visualizations on the same data table without configuration, comparable to Qlik selections.
- Spec deviation, same as Qlik: no recession shading, and the state view uses a sorted bar chart rather than a choropleth. The state bar chart shows the 1990-2026 average per state rather than the latest month, since a latest-value expression in the Spotfire UI was not worth the time.

## Setup and connectivity

Scores are 1 to 5 from building the identical three-page dashboard in both tools against docs/dashboard-spec.md.

| Dimension | Qlik | Spotfire | Notes |
|---|---|---|---|
| Getting to a working environment | 5 | 2 | Qlik: browser signup, building within minutes. Spotfire: Windows-only installer, which meant provisioning a Windows Server on EC2 and working over RDP from a Mac. |
| Loading the warehouse extracts | 4 | 4 | Even. Both took the same four CSVs without complaint. Neither cloud trial could reach a local Postgres, so published extracts were the practical path for both. |
| Data model and association handling | 5 | 2 | Qlik associated the marts on the shared year_month automatically. Spotfire treats each file as an independent table with a per-visualization table selector, and new charts silently inherit the last active table. |
| Load performance | 4 | 4 | Even at this scale. 36k rows is small for both engines. |

## Dashboard build

| Dimension | Qlik | Spotfire | Notes |
|---|---|---|---|
| KPI tiles (page 1) | 4 | 4 | Qlik's KPI object needed set-analysis expressions for latest-value logic. Spotfire's KPI chart gave sparklines for free but defaults to Sum, which has to be corrected to Avg on every tile. |
| Time series (page 2) | 3 | 4 | Spotfire wins on individual scales per measure ("One scale for each color"), which made a five-measure chart readable. Qlik's equivalent stayed on a single scale, flattening the z-scores. |
| Mixed-magnitude readability | 2 | 5 | The clearest single difference in the whole build. |
| Cross-filtering (page 3) | 5 | 4 | Qlik's selection model is global and needed no setup. Spotfire's marking works well but is scoped per data table. |
| Spec fidelity | 3 | 3 | Both missed recession shading and the choropleth; both substituted a sorted bar chart plus interaction. |
| Automation and repeatability | 5 | 1 | Qlik's Engine JSON-RPC and REST APIs allowed the entire app (sheets, charts, data load, reload) to be created from a script. The Spotfire trial exposes no authoring API, so all three pages were built by hand. |

## Analyst experience

| Dimension | Qlik | Spotfire | Notes |
|---|---|---|---|
| Learning curve | 3 | 4 | Spotfire's property panel is more discoverable. Qlik's power sits in set analysis, which is a real language to learn. |
| Expression language | 4 | 3 | Qlik set analysis is more capable once learned; Spotfire's OVER/aggregation syntax handles simpler cases with less ceremony. |
| Defaults that fight you | 4 | 2 | Spotfire defaults to Sum aggregation and Year-binned dates, both wrong for monthly rate data and both silent. |
| Sharing and export | 4 | 3 | Qlik is browser-native and shareable by link. Spotfire files live on the desktop unless published to a server. |

## Verdict

- **Best for executive dashboards:** Qlik. Browser-native, shareable by link, and the associative model means a business user clicking around does not break anything.
- **Best for exploratory analysis:** Spotfire. Individual scales, faster property panel, and better handling of measures that live on different magnitudes.
- **Best for a Postgres warehouse stack:** Qlik, mainly because the whole app can be built and rebuilt programmatically. A dashboard defined in code is a dashboard that can be version-controlled and recreated.
- **What I would tell a client choosing between them:** if the deliverable is a governed dashboard that many people consume and that a team needs to rebuild reliably, Qlik. If the deliverable is an analyst workbench for interrogating data with awkward scales, Spotfire. The deciding question is not which renders prettier charts, it is whether the dashboards need to be reproducible artifacts or exploratory workspaces.

## What I would do differently

- Compute latest-value and 12-month-change columns in the warehouse rather than in either BI tool. Both tools made that logic harder than the SQL would have been, and doing it once upstream would have kept the two dashboards identical by construction.
- Add an explicit recession-shading column (start and end month per NBER episode) to the mart so both tools can draw bands without native support.
