# Roadmap

Small sprints grouped into four phases. Each sprint is one focused work session (roughly 2 to 5 hours) with a definition of done. Check items off as they land; one commit (or a few) per sprint.

**Timing rule:** the Qlik Sense and Spotfire trials run about 30 days each. Do not start Sprint 4 until Sprints 1 to 3 are done, then finish Sprints 4 to 6 inside one trial window.

---

## Phase A: Data foundation

### Sprint 0: Scaffold and planning ✅ (done 2026-07-28)
- [x] Repo scaffolded: ETL modules, schema, docs, workflow
- [x] Planning docs: requirements, wireframes, user flows, tech stack, file structure
- [x] Upstream reviewed (docs/upstream-review.md)

### Sprint 1: First full pipeline run
Goal: real data flowing end to end on this machine.
- [ ] Get a free FRED API key; `cp .env.example .env` and fill it in
- [ ] Install Docker Desktop (pending on this Mac) or point `.env` at a local Postgres
- [ ] `docker compose up -d`, `pip install -r requirements.txt`
- [ ] `python -m etl.run_pipeline --skip-brief` and fix any runtime issues
- [ ] Sanity-query the marts (latest month present, pressure score non-null, 51 states)
- [ ] Commit the first `reports/validation_report.md`

**Done when:** all pipeline stages pass and `mart_debt_cycle_monthly` has data through the latest FRED month.

### Sprint 2: Dalio metric expansion (adopted from upstream)
Goal: fold in the upstream project's cycle framing and market-price indicators.
- [ ] Add series to `etl/config.py`: real GDP growth (A191RL1Q225SBEA), S&P 500 (SP500), Case-Shiller national home prices (CSUSHPINSA), 10Y Treasury yield (DGS10), trade-weighted dollar (DTWEXBGS)
- [ ] Add `cycle_lens` (deflationary / inflationary / both) to `dim_series` and the series catalog
- [ ] Extend `mart_debt_cycle_monthly` with the new columns (+ home price yoy, S&P yoy)
- [ ] Re-run pipeline; update README indicator counts and dashboard-spec if pages change
- [ ] Note in upstream-review.md that the adoption landed

**Done when:** validation passes with ~70 series and the new columns populate.

---

## Phase B: Publish and automate

### Sprint 3: GitHub + live automation
Goal: the repo is public and refreshes itself.
- [ ] Decide the GitHub repo name (avoid colliding with the upstream name; e.g. `debt-cycle-bi`)
- [ ] Push; verify wireframe SVGs and mermaid charts render
- [ ] Add `FRED_API_KEY` secret; run the workflow via manual dispatch until green
- [ ] Optional: AWS secrets so the workflow commits a Bedrock brief; generate the first `reports/briefs/YYYY-MM.md`
- [ ] Add repo link to resume header / portfolio

**Done when:** a manually dispatched Actions run completes and commits a fresh validation report.

---

## Phase C: BI build (trial clock starts here)

### Sprint 4: Qlik Sense dashboard
- [ ] Start Qlik Sense trial; connect to Postgres (or export marts to CSV if the cloud trial can't reach localhost; note the workaround in comparison.md)
- [ ] Build pages 1 to 3 per docs/dashboard-spec.md and the wireframes
- [ ] Screenshots of each page to docs/screenshots/qlik-*
- [ ] Log observations in comparison.md while fresh

### Sprint 5: Spotfire dashboard
- [ ] Start Spotfire trial; same three pages, same spec
- [ ] Screenshots to docs/screenshots/spotfire-*
- [ ] Log observations in comparison.md

### Sprint 6: Comparison and polish
- [ ] Fill every comparison.md table and write the verdict section
- [ ] Embed the best screenshots in the README
- [ ] Read the whole repo once as a stranger; fix anything confusing

**Done when:** comparison.md has no empty cells and the README shows both tools' dashboards.

---

## Phase D: Career deliverables

### Sprint 7: Resume and interview prep
- [ ] Swap AquaSense for this project's bullets on the PwC resume variant
- [ ] Write the STAR story: requirement -> pipeline -> validation catch -> dashboards -> comparison verdict
- [ ] Prepare the 2-minute demo walk-through (README -> validation report -> dashboard screenshots -> brief)
- [ ] Rehearse the "why these numbers" answer for pressure score components and z-score window

**Done when:** the resume variant is updated and the demo story is rehearsed once out loud.
