# Upstream Review: SimSimButDifferent/debt-cycles-tracker

Reviewed 2026-07-28. The upstream project is a web dashboard for metrics from Ray Dalio's "Principles for Navigating Big Debt Crises": Next.js + React + TypeScript frontend, Chart.js visualizations, and FRED data cached in PostgreSQL through Prisma. This project takes its subject and its data-source idea, credits it in the README, and rebuilds everything as a BI engineering pipeline. Nothing is forked; no upstream code is vendored.

## What we adopt

1. **The Dalio framing.** Upstream categorizes metrics into deflationary-cycle, inflationary-cycle, and shared indicators. Adopted as a `cycle_lens` attribute on `dim_series` so dashboards can group indicators the same way (landed in Sprint 2).
2. **Market-price indicators we initially lacked.** Upstream tracks asset prices alongside credit data. Added: real GDP growth, S&P 500, Case-Shiller home prices, 10-year Treasury yield, and the trade-weighted dollar index (landed in Sprint 2).
3. **FRED + Postgres as the backbone.** Same core idea; we keep it.

## What we deliberately do differently

| Upstream | This project | Why |
|---|---|---|
| Custom React/Chart.js frontend | Qlik Sense + Spotfire dashboards | The target role names these tools; the BI layer is the point |
| Prisma cache of raw series | Star schema + derived monthly marts | Data architecture story: yoy, z-scores, composite score computed once in the warehouse |
| No validation layer | Hard data-quality gate + committed reports | The JD's "validate data quality and integrity" line, made literal |
| Manual refresh scripts | Scheduled GitHub Actions refresh | Managed-service shape |
| Educational static text | LLM executive brief from live warehouse numbers | Stakeholder deliverable, not documentation |
| National US data only | Plus 51-state drill-down | Micro analysis next to macro |
