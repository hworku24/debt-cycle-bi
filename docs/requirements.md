# Scope

What I wanted this thing to answer, what I decided to leave out, and the questions each dashboard page has to satisfy. Written before the build so I had something to check the finished dashboards against.

## What I am actually trying to see

The US is carrying federal debt above 120% of GDP, household debt service is creeping back up, and credit card delinquencies have been rising since 2022. Any one of those numbers is easy to find. What is hard to see is the shape of them together: whether current stress is unusual by historical standards, whether credit is tightening or loosening right now, and which parts of the country are diverging from the national picture.

The lens is the split between deflationary and inflationary debt cycles: whether a debt burden gets heavier because prices and incomes are falling, or whether the currency absorbs the damage instead. The point is not to predict a recession. It is to have a defensible monthly answer to "is pressure building, and where."

## Questions each page has to answer

1. At a glance, how do current conditions compare to a year ago?
2. Where are we in the long debt cycle relative to the last 35 years?
3. Are credit conditions tightening or loosening right now?
4. Which states are diverging from the national picture?
5. What changed since last month, and what is worth watching next?

## What it does

- Pulls 70 FRED series (19 national debt-cycle and market indicators, 51 state unemployment series) from 1990 to present
- Validates before loading: schema, duplicates, continuity, plausible ranges, staleness
- Loads a PostgreSQL star schema with derived monthly marts (yoy changes, rolling z-scores, yield-inversion flag, composite cycle pressure score)
- Feeds a three-page dashboard built identically in Qlik Sense and Spotfire
- Generates a monthly one-page summary from the warehouse numbers using Claude on Bedrock
- Refreshes itself monthly through GitHub Actions and commits the resulting reports

## What it deliberately does not do

- **No forecasting.** It describes current and historical conditions. It does not predict recessions, and the composite score is an index, not a model.
- **Monthly grain only.** Daily and weekly series are averaged into months, so intra-month moves are invisible.
- **FRED only.** No commercial data feeds, so series availability and revisions follow whatever FRED publishes.
- **No investment advice.** The monthly summary describes what moved. That is all it does.
- **Dashboards live on trial accounts** and will expire, which is why the screenshots and the written comparison are in the repo.

## Design rules I held myself to

- History back to 1990 so at least three full cycles are visible.
- Derived indicators (yoy, z-scores, composite score) computed once in the warehouse, never in the BI tool, so both dashboards show identical numbers and the logic stays version-controlled.
- The pipeline halts on critical data-quality failures rather than publishing bad numbers, and the validation report gets committed either way.
