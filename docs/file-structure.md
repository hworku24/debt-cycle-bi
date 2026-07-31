# File Structure

Planned layout, written before implementation and kept current.

```
debt-cycle-bi-tracker/
├── README.md                    # Overview, architecture, quickstart
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Local Postgres 16
├── .env.example                 # Config template (DB, FRED key, AWS)
├── .github/
│   └── workflows/
│       └── monthly-refresh.yml  # Scheduled pipeline + report commit
├── sql/
│   └── schema.sql               # Star schema + marts (dropped and rebuilt each run)
├── etl/
│   ├── config.py                # Series catalog, DB config, validation thresholds
│   ├── extract.py               # FRED API -> data/raw/fred/*.json
│   ├── validate.py              # Data-quality gate -> reports/validation_report.md
│   ├── transform.py             # Frames -> dims, facts, monthly marts
│   ├── load.py                  # Bulk load + post-load reconciliation
│   ├── brief.py                 # Bedrock summary writer
│   └── run_pipeline.py          # Orchestrator (extract -> validate -> transform -> load -> brief)
├── data/
│   └── raw/fred/                # Raw API payloads (gitignored)
├── reports/
│   ├── validation_report.md     # Committed by the monthly workflow
│   └── briefs/                  # Monthly written summaries
└── docs/
    ├── requirements.md          # What it answers, what it leaves out
    ├── tech-stack.md            # Tools, languages, libraries and why
    ├── file-structure.md        # This file
    ├── user-flow.md             # Executive + analyst flow charts
    ├── dashboard-spec.md        # The spec both BI tools implement
    ├── comparison.md            # Qlik Sense vs Spotfire findings
    ├── wireframes/              # SVG wireframes for the three dashboard pages
    └── screenshots/             # Final dashboards from both tools
```

Conventions: pipeline stages are one module each with a `run()` entry point so they can run standalone (`python -m etl.extract`) or via the orchestrator; everything generated is either gitignored (`data/raw/`) or deliberately committed as an audit trail (`reports/`).
