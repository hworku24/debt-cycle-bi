# Roadmap

Work is broken into short sprints, roughly one working session each. Sprints 4 through 6 depend on BI trial accounts that expire after 30 days, so don't start those until everything before them is done.

## Closing out a sprint

Every sprint ends with a review pass before its final commit. A senior engineer is the audience for this repo, so anything touched this sprint gets read once with these checks:

- no em-dashes or en-dashes anywhere
- no inflated wording or filler jargon (leverage, robust, seamless, comprehensive, cutting-edge, and the like); plain words over impressive ones
- no templated or repetitive structure that reads machine-written
- every number, series id, and claim in the docs matches the code
- would I be comfortable explaining this line by line in a code review

## Sprint 0: scaffold (done)

Repo structure, ETL modules, schema, planning docs, upstream review. Committed 2026-07-28.

## Sprint 1: first end-to-end run (done)

Get real data flowing on this machine.

- [x] FRED API key into `.env` (free, fred.stlouisfed.org)
- [x] Docker Desktop was already installed; `docker compose up -d`
- [x] `pip install -r requirements.txt`
- [x] `python -m etl.run_pipeline --skip-brief`. First contact with live data surfaced three real issues: numpy scalars need unwrapping before psycopg2 inserts, TOTALSL is reported in millions not billions, and TDSP has no data before 2005 so leading gaps had to be excluded from the missing-value check
- [x] Spot check the marts: data through 2026-07, pressure score 0.67, 51 states, 54,394 fact rows
- [x] Commit the first validation report. Six warnings remain, all staleness: five quarterly series sitting between normal releases, plus HDTGPDUSQ163N which has stopped updating (see backlog)

Exit criteria met: all pipeline stages pass against live FRED data.

## Sprint 2: metric expansion (done)

Add the market-price indicators the upstream project tracks and we skipped, plus its cycle categorization.

- [x] New series in config: A191RL1Q225SBEA (real GDP growth), SP500, CSUSHPINSA (Case-Shiller), DGS10, DTWEXBGS (dollar index)
- [x] `cycle_lens` column on dim_series (deflationary / inflationary / both)
- [x] New mart columns, including home price yoy and S&P yoy
- [x] Series counts updated in README, requirements, and the dashboard spec (markets panel added to page 2)
- [x] Short-history and slow-release series: SP500 and the other daily series skip the monthly continuity check by design; Case-Shiller's 2-month release lag got a staleness_days override
- [x] Re-run against live data: sp500_yoy 19.0%, home_price_index_yoy 1.3% in the latest month, cycle_lens populated for all 70 series

Exit criteria: validation passes with the expanded catalog, new columns populated.

## Sprint 3: publish and automate (done)

- [x] Repo name: debt-cycle-bi, public, distinct from the upstream project's name
- [x] Pushed; SVG wireframes and mermaid diagrams render on GitHub
- [x] FRED_API_KEY repo secret added; workflow went green on the first manual dispatch and committed a refreshed validation report as github-actions[bot]
- [ ] AWS credentials for the Bedrock brief. Not set up on this machine yet; the pipeline runs without it and the README says the step is optional
- [x] Repo linked from the resume

Exit criteria met: a manually triggered Actions run completed and committed a fresh validation report.

## Sprint 4: Qlik dashboard

Trial clock starts here.

- [ ] Start the Qlik Sense trial
- [ ] Connect to Postgres. If the cloud trial can't reach localhost, export the marts to CSV and note the workaround in comparison.md
- [ ] Build the three pages against docs/dashboard-spec.md and the wireframes
- [ ] Screenshots into docs/screenshots/, prefixed qlik-
- [ ] Write down observations in comparison.md while they're fresh, not at the end

## Sprint 5: Spotfire dashboard

Same three pages, same spec.

- [ ] Start the Spotfire trial
- [ ] Build pages 1 to 3
- [ ] Screenshots prefixed spotfire-
- [ ] More comparison.md notes

## Sprint 6: comparison writeup

- [ ] Fill in every table in comparison.md and write the verdict
- [ ] Put the best screenshots in the README
- [ ] Full read-through of the repo with fresh eyes, fix anything that doesn't explain itself

Exit criteria: no empty cells in comparison.md.

## Backlog (not scheduled)

- Replace HDTGPDUSQ163N. The validation gate flagged it 483 days stale on the first live run; the IMF-sourced household debt to GDP series has effectively stopped updating. Candidate replacement: BIS credit-to-households series (QUSPAM770A) or computing the ratio from Z.1 components.

## Sprint 7: interview prep

- [ ] Swap AquaSense out for this project on the PwC resume variant
- [ ] Write out the project story: the requirement, the pipeline, what validation caught, the two dashboards, the verdict
- [ ] Practice a short demo path: README, validation report, dashboard screenshots, a brief
- [ ] Be ready to defend the choices: why these four pressure components, why a 10 year z-score window, why compute in the warehouse instead of the BI tool
