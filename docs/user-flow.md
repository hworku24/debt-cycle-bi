# User Flow

Two ways I actually use this: the monthly read (open the dashboard, see what moved) and the maintenance loop (run the pipeline, fix what broke). GitHub renders the diagrams below natively.

## Monthly read

```mermaid
flowchart TD
    A[Monthly refresh lands in the repo] --> B[Open dashboard]
    B --> C[Page 1: Current Conditions KPIs]
    C --> D{Anything moved?}
    D -- No --> E[Skim the summary, done]
    D -- Yes --> F[Page 2: Debt Cycle View]
    F --> G[Check which component z-scores drove the pressure score]
    G --> H{Regional angle?}
    H -- Yes --> I[Page 3: State Drill-Down]
    I --> J[Select state, compare vs national]
    H -- No --> K[Read the monthly summary]
    J --> K
    K --> L[Note what to watch next month]
```

## Maintenance loop

```mermaid
flowchart TD
    A[Clone repo] --> B[cp .env.example .env, add FRED key]
    B --> C[docker compose up -d]
    C --> D[python -m etl.run_pipeline]
    D --> E{Validation gate}
    E -- Critical failure --> F[Read reports/validation_report.md]
    F --> G[Fix source config or accept revision] --> D
    E -- Pass --> H[Star schema + marts loaded to Postgres]
    H --> I[Connect Qlik Sense / Spotfire]
    I --> J[Build or refresh dashboards per docs/dashboard-spec.md]
    H --> K[Bedrock brief written to reports/briefs/]
    L[GitHub Actions, 5th of month] --> D
```
