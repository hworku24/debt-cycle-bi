# Scope

This document covers what the tracker is meant to answer, what it includes, and what I chose not to build.

## Goal

The Debt Cycle BI Tracker brings federal debt, household credit, interest rates, inflation, market data, and unemployment into one monthly view.

Most of these indicators are already available through FRED, but usually as separate charts. The goal here is to see how they are moving together and answer a few basic questions:

* Is financial pressure building or easing?
* Are current conditions unusual compared with recent history?
* Which states are moving differently from the national trend?

The indicators are also tagged using Ray Dalio's distinction between deflationary and inflationary debt cycles. This is mainly used as an organizing framework for the dashboard.

The tracker is meant to describe current conditions, not predict what happens next.

## Questions the dashboard should answer

1. How do current conditions compare with a year ago?
2. How do the latest readings compare with their historical ranges?
3. Are credit conditions tightening or easing?
4. Which states differ most from the national unemployment rate?
5. What changed in the latest update?
6. Which indicators are worth watching next month?

## What is included

The project:

* Pulls 70 FRED series, including 19 national indicators and 51 state unemployment series
* Uses data from 1990 through the latest available release
* Checks the data for missing fields, duplicate dates, gaps, unusual values, and stale series
* Loads the results into PostgreSQL
* Builds monthly national and state-level marts
* Calculates year-over-year changes, rolling z-scores, yield-curve inversion flags, and a composite pressure score
* Uses the same dashboard requirements for Qlik Sense and TIBCO Spotfire
* Generates a monthly written brief using Claude through Amazon Bedrock
* Refreshes the data and reports monthly through GitHub Actions

## What is not included

### Forecasting

The tracker does not predict recessions, defaults, market returns, or future interest rates.

The composite pressure score is a summary of current conditions. It is not a forecast or probability.

### Daily analysis

The dashboard works at a monthly level.

Daily and weekly series are rolled up into monthly values, so short-term moves within a month are not shown.

### Other data sources

The project only uses data available through FRED.

It does not include commercial feeds, private credit data, company financial statements, or alternative datasets. Release delays and historical revisions depend on what FRED publishes.

### Investment advice

The dashboard and monthly brief describe changes in the data. They do not provide trading, investment, or personal financial advice.

### Permanent dashboard hosting

The Qlik Sense and Spotfire dashboards were built using trial accounts.

Screenshots, specifications, and implementation notes are included in the repository so the work is still documented after the trials expire.

## Design rules

### Historical coverage

Where possible, each series starts in 1990.

This gives enough history to compare current readings across different recessions, expansions, and interest-rate environments.

### Shared calculations

Derived metrics are calculated in the pipeline or warehouse instead of separately in each BI tool.

These include:

* Year-over-year changes
* Rolling averages and standard deviations
* Z-scores
* Yield-curve inversion flags
* Composite pressure scores

Doing the calculations once keeps the Qlik and Spotfire dashboards consistent and makes the logic easier to review in code.

### Data validation

Critical validation failures stop the pipeline before the data is published.

Warnings do not always stop the run, but they are included in the validation report.

A report is written every time the pipeline runs, including failed runs.

### Same dashboard requirements

Both dashboard versions use the same:

* Data extracts
* Page structure
* Indicators
* Date ranges
* Filters
* KPI definitions
* Comparison periods

Some visuals may differ when one platform does not support the original design. Those changes are documented in the platform comparison.

### Reproducibility

The repository should contain everything needed to rerun the pipeline and understand how the dashboards were built.

