# User Flow

Two user types interact with the project: the **executive** (consumes dashboards and the monthly brief) and the **analyst/maintainer** (runs and extends the pipeline). GitHub renders the charts below natively.

## Executive flow

```mermaid
flowchart TD
    A[Monthly refresh email or repo notification] --> B[Open dashboard]
    B --> C[Page 1: Current Conditions KPIs]
    C --> D{Anything moved?}
    D -- No --> E[Skim monthly brief, done]
    D -- Yes --> F[Page 2: Debt Cycle View]
    F --> G[Check which component z-scores drove the pressure score]
    G --> H{Regional angle?}
    H -- Yes --> I[Page 3: State Drill-Down]
    I --> J[Select state, compare vs national]
    H -- No --> K[Read monthly brief for narrative]
    J --> K
    K --> L[Share brief with team / decide what to watch next month]
```

## Analyst / maintainer flow

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
