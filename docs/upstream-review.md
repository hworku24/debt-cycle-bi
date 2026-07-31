# Upstream Review: SimSimButDifferent/debt-cycles-tracker

Reviewed 2026-07-28. The upstream project is a web dashboard for metrics from Ray Dalio's "Principles for Navigating Big Debt Crises": Next.js + React + TypeScript frontend, Chart.js visualizations, and FRED data cached in PostgreSQL through Prisma. This project takes its subject and its data-source idea, credits it in the README, and rebuilds it as a warehouse-plus-BI stack instead of a web app. Nothing is forked; no upstream code is vendored.

## What I took from it

1. **The Dalio framing.** Upstream categorizes metrics into deflationary-cycle, inflationary-cycle, and shared indicators. Adopted as a `cycle_lens` attribute on `dim_series` so dashboards can group indicators the same way (landed in Sprint 2).
2. **Market-price indicators I had skipped.** Upstream tracks asset prices alongside credit data. Added: real GDP growth, S&P 500, Case-Shiller home prices, 10-year Treasury yield, and the trade-weighted dollar index (landed in Sprint 2).
3. **FRED plus Postgres as the backbone.** Same core idea, kept.

## What I did differently

| Upstream | This project | Why |
|---|---|---|
| Custom React/Chart.js frontend | Qlik Sense + Spotfire dashboards | I did not want to write a frontend; I wanted to compare two BI tools on the same spec |
| Prisma cache of raw series | Star schema + derived monthly marts | yoy, z-scores, and the composite score get computed once, in one place, so every chart agrees |
| No validation layer | Hard data-quality gate + committed reports | FRED series get revised, renamed, and abandoned; I wanted to know before bad numbers reached a chart |
| Manual refresh scripts | Scheduled GitHub Actions refresh | If I have to remember to run it, I will stop running it |
| Educational static text | Monthly summary generated from live warehouse numbers | I wanted a written read on what moved, not a glossary |
| National US data only | Plus 51-state drill-down | National averages hide how differently states are doing |
