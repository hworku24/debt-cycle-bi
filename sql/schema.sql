-- Star schema for the Debt Cycle BI Tracker.
-- Rebuilt on every pipeline run; FRED is the system of record.

DROP TABLE IF EXISTS mart_state_monthly;
DROP TABLE IF EXISTS mart_debt_cycle_monthly;
DROP TABLE IF EXISTS fact_observations;
DROP TABLE IF EXISTS dim_series;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key    INT PRIMARY KEY,          -- YYYYMMDD
    full_date   DATE NOT NULL UNIQUE,
    year        INT NOT NULL,
    quarter     INT NOT NULL,
    month       INT NOT NULL,
    month_name  TEXT NOT NULL,
    year_month  TEXT NOT NULL             -- 'YYYY-MM'
);

CREATE TABLE dim_series (
    series_id   TEXT PRIMARY KEY,         -- FRED id
    series_name TEXT NOT NULL,
    category    TEXT NOT NULL,            -- debt / credit / rates / prices / money / labor / sentiment / cycle
    frequency   TEXT NOT NULL,            -- D / W / M / Q (native)
    units       TEXT NOT NULL,
    geography   TEXT NOT NULL,            -- 'US' or two-letter state code
    cycle_lens  TEXT NOT NULL             -- deflationary / inflationary / both (Dalio framing)
);

-- One row per series per native-frequency observation date.
CREATE TABLE fact_observations (
    series_id   TEXT NOT NULL REFERENCES dim_series(series_id),
    obs_date    DATE NOT NULL,
    value       NUMERIC,
    PRIMARY KEY (series_id, obs_date)
);

-- Wide monthly mart the BI tools read directly. All national series resampled
-- to month grain; *_yoy are year-over-year % changes; *_z are z-scores vs a
-- rolling 10-year window; cycle_pressure_score averages the stress z-scores.
CREATE TABLE mart_debt_cycle_monthly (
    year_month            TEXT PRIMARY KEY,   -- 'YYYY-MM'
    month_date            DATE NOT NULL,
    household_debt_gdp    NUMERIC,
    federal_debt_gdp      NUMERIC,
    debt_service_ratio    NUMERIC,
    cc_delinquency        NUMERIC,
    mortgage_delinquency  NUMERIC,
    consumer_credit       NUMERIC,
    consumer_credit_yoy   NUMERIC,
    fedfunds              NUMERIC,
    mortgage_rate_30y     NUMERIC,
    yield_spread_10y2y    NUMERIC,
    yield_inverted        BOOLEAN,
    cpi                   NUMERIC,
    cpi_yoy               NUMERIC,
    m2                    NUMERIC,
    m2_yoy                NUMERIC,
    unemployment          NUMERIC,
    consumer_sentiment    NUMERIC,
    recession             BOOLEAN,
    gdp_growth            NUMERIC,
    sp500                 NUMERIC,
    sp500_yoy             NUMERIC,
    home_price_index      NUMERIC,
    home_price_index_yoy  NUMERIC,
    treasury_10y          NUMERIC,
    dollar_index          NUMERIC,
    household_debt_gdp_z  NUMERIC,
    debt_service_ratio_z  NUMERIC,
    cc_delinquency_z      NUMERIC,
    fedfunds_z            NUMERIC,
    cycle_pressure_score  NUMERIC
);

-- State-level drill-down (microeconomic view).
CREATE TABLE mart_state_monthly (
    year_month        TEXT NOT NULL,
    state             TEXT NOT NULL,
    unemployment_rate NUMERIC,
    PRIMARY KEY (year_month, state)
);

CREATE INDEX idx_fact_obs_date   ON fact_observations(obs_date);
CREATE INDEX idx_state_monthly   ON mart_state_monthly(state);
