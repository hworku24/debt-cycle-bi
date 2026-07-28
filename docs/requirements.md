# Stakeholder Requirements

This document simulates the requirements-gathering step of a client BI engagement: a stakeholder brief translated into concrete, testable requirements. The dashboards in both platforms are built against this document, and the platform comparison scores each tool on how well it satisfied it.

## Client persona

A strategy team at a mid-size investment advisory wants a monthly view of where the US economy sits in the debt cycle to inform market development strategy and client positioning. They are non-technical consumers of dashboards and a one-page monthly memo.

## Business questions

1. Where are we in the long-term debt cycle relative to history? (macroeconomic analysis)
2. Are credit conditions tightening or loosening right now?
3. Is recession risk rising, and what do the leading indicators say?
4. Which states are diverging from the national picture? (microeconomic analysis)
5. What changed since last month, and what should we watch next?

## Functional requirements

| ID | Requirement | Delivered by |
|---|---|---|
| R1 | Refresh all indicators monthly without manual work | GitHub Actions scheduled pipeline |
| R2 | Validate data quality and integrity before any number reaches a dashboard | etl/validate.py gate + committed validation report |
| R3 | Single warehouse both BI tools read from, identical numbers in both | PostgreSQL star schema + monthly marts |
| R4 | Executive KPI view: current conditions at a glance | Dashboard page 1 (see dashboard-spec.md) |
| R5 | Long-term cycle view with recessions shaded | Dashboard page 2 |
| R6 | State-level drill-down for regional divergence | Dashboard page 3 |
| R7 | Monthly plain-language memo grounded in the warehouse numbers | LLM executive brief (etl/brief.py) |

## Non-functional requirements

- History from 1990 so at least three full cycles are visible.
- Derived indicators (year-over-year changes, z-scores, composite score) computed once in the warehouse, never in the BI tool, so both tools show identical values.
- Pipeline halts on critical data-quality failures rather than publishing bad numbers.
