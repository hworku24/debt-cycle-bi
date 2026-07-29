# Roadmap

Work is broken into short sprints, roughly one working session each. Sprints 4 through 6 depend on BI trial accounts that expire after 30 days, so don't start those until everything before them is done.

## Sprint 0: scaffold (done)

Repo structure, ETL modules, schema, planning docs, upstream review. Committed 2026-07-28.

## Sprint 1: first end-to-end run

Get real data flowing on this machine.

- [ ] FRED API key into `.env` (free, fred.stlouisfed.org)
- [ ] Install Docker Desktop, or point `.env` at an existing local Postgres
- [ ] `docker compose up -d`
- [ ] `pip install -r requirements.txt`
- [ ] `python -m etl.run_pipeline --skip-brief`, fix whatever breaks on first contact with live data
- [ ] Spot check the marts: latest month present, pressure score populated, 51 states in mart_state_monthly
- [ ] Commit the first validation report

Exit criteria: all pipeline stages pass against live FRED data.

## Sprint 2: metric expansion

Add the market-price indicators the upstream project tracks and we skipped, plus its cycle categorization.

- [ ] New series in config: A191RL1Q225SBEA (real GDP growth), SP500, CSUSHPINSA (Case-Shiller), DGS10, DTWEXBGS (dollar index)
- [ ] `cycle_lens` column on dim_series (deflationary / inflationary / both)
- [ ] New mart columns, including home price yoy and S&P yoy
- [ ] Re-run pipeline, update the series counts in README and the dashboard spec if the pages change
- [ ] SP500 only goes back about 10 years on FRED. Check whether that trips the continuity check and decide how to handle it

Exit criteria: validation passes with the expanded catalog, new columns populated.

## Sprint 3: publish and automate

- [ ] Pick the GitHub repo name. The Desktop folder is named after the upstream repo; the public repo should not be, to avoid looking like a fork
- [ ] Push, then check that the SVG wireframes and mermaid diagrams render on GitHub
- [ ] Add FRED_API_KEY as a repo secret, run the workflow by hand until it goes green
- [ ] AWS secrets if I want the workflow committing briefs. Optional, the pipeline works without it
- [ ] Generate one brief locally and commit it so reviewers can see an example
- [ ] Link the repo from resume and portfolio

Exit criteria: a manually triggered Actions run completes and commits a fresh validation report.

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

## Sprint 7: interview prep

- [ ] Swap AquaSense out for this project on the PwC resume variant
- [ ] Write out the project story: the requirement, the pipeline, what validation caught, the two dashboards, the verdict
- [ ] Practice a short demo path: README, validation report, dashboard screenshots, a brief
- [ ] Be ready to defend the choices: why these four pressure components, why a 10 year z-score window, why compute in the warehouse instead of the BI tool
