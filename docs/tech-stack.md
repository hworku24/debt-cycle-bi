# Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.12 | ETL, transforms, orchestration |
| Language | SQL (PostgreSQL dialect) | Schema definition, marts, reconciliation queries |
| Data source | FRED API | Free, authoritative US macro data with a stable JSON API |
| Warehouse | PostgreSQL 16 | Star schema + marts; both BI tools connect natively |
| Local infra | Docker Compose | One-command reproducible Postgres |
| BI tool 1 | Qlik Sense (cloud trial) | Named in the target role; associative data model |
| BI tool 2 | TIBCO Spotfire (cloud trial) | Named in the target role; strong analytical charting |
| AI | Claude on Amazon Bedrock (`anthropic` SDK) | Monthly executive brief generated from warehouse metrics |
| Automation | GitHub Actions | Monthly scheduled refresh with a containerized Postgres service |

## Python libraries

| Library | Used for |
|---|---|
| pandas / numpy | Parsing FRED payloads, resampling, yoy and z-score derivations |
| requests | FRED API calls |
| psycopg2-binary | Postgres bulk loads (`execute_values`) and reconciliation checks |
| python-dotenv | Local configuration via `.env` |
| tabulate | Markdown tables in the LLM prompt |
| anthropic[bedrock] | Claude via the Bedrock client for the executive brief |

## Deliberate non-choices

- **No Airflow/Dagster.** A monthly single-DAG pipeline doesn't justify an orchestrator; GitHub Actions cron is enough and one less system to run.
- **No dbt.** The transform layer is small enough to keep in pandas + one schema file; dbt would be the right move if the mart count grew.
- **No FastAPI/frontend.** The BI tools are the presentation layer by design; that's the point of the project.
