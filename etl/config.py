import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRED_DIR = PROJECT_ROOT / "data" / "raw" / "fred"
REPORTS_DIR = PROJECT_ROOT / "reports"
BRIEFS_DIR = REPORTS_DIR / "briefs"
SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema.sql"

DB = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "debt_cycle"),
    "user": os.getenv("POSTGRES_USER", "bi_user"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
}

FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Claude on Amazon Bedrock, used for the monthly executive brief. The id is a
# cross-region inference profile on the classic bedrock-runtime endpoint.
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BRIEF_MODEL = os.getenv("BRIEF_MODEL", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")

# History window loaded into the warehouse.
START_DATE = "1990-01-01"

# National macro series. mart_column is the wide-mart column the series feeds;
# transform derives *_yoy and *_z columns from these. cycle_lens tags which kind
# of debt cycle a series speaks to (deflationary, inflationary, or both), the
# split Dalio uses in his work on big debt crises.
# staleness_days overrides the per-frequency default for series with slow
# release schedules.
NATIONAL_SERIES = {
    "HDTGPDUSQ163N": {"name": "Household debt to GDP",            "category": "debt",       "frequency": "Q", "units": "% of GDP",  "mart_column": "household_debt_gdp",   "cycle_lens": "deflationary"},
    "GFDEGDQ188S":   {"name": "Federal debt to GDP",              "category": "debt",       "frequency": "Q", "units": "% of GDP",  "mart_column": "federal_debt_gdp",     "cycle_lens": "both"},
    "TDSP":          {"name": "Household debt service ratio",     "category": "debt",       "frequency": "Q", "units": "%",         "mart_column": "debt_service_ratio",   "cycle_lens": "both"},
    "DRCCLACBS":     {"name": "Credit card delinquency rate",     "category": "credit",     "frequency": "Q", "units": "%",         "mart_column": "cc_delinquency",       "cycle_lens": "deflationary"},
    "DRSFRMACBS":    {"name": "Mortgage delinquency rate",        "category": "credit",     "frequency": "Q", "units": "%",         "mart_column": "mortgage_delinquency", "cycle_lens": "deflationary"},
    "TOTALSL":       {"name": "Total consumer credit",            "category": "credit",     "frequency": "M", "units": "$M",        "mart_column": "consumer_credit",      "cycle_lens": "deflationary", "bounds": (0, 10_000_000), "staleness_days": 100},
    "FEDFUNDS":      {"name": "Federal funds rate",               "category": "rates",      "frequency": "M", "units": "%",         "mart_column": "fedfunds",             "cycle_lens": "both"},
    "MORTGAGE30US":  {"name": "30-year mortgage rate",            "category": "rates",      "frequency": "W", "units": "%",         "mart_column": "mortgage_rate_30y",    "cycle_lens": "deflationary"},
    "T10Y2Y":        {"name": "10Y minus 2Y Treasury spread",     "category": "rates",      "frequency": "D", "units": "pp",        "mart_column": "yield_spread_10y2y",   "cycle_lens": "deflationary"},
    "DGS10":         {"name": "10-year Treasury yield",           "category": "rates",      "frequency": "D", "units": "%",         "mart_column": "treasury_10y",         "cycle_lens": "deflationary"},
    "CPIAUCSL":      {"name": "CPI, all urban consumers",         "category": "prices",     "frequency": "M", "units": "index",     "mart_column": "cpi",                  "cycle_lens": "both"},
    "M2SL":          {"name": "M2 money stock",                   "category": "money",      "frequency": "M", "units": "$B",        "mart_column": "m2",                   "cycle_lens": "inflationary"},
    "UNRATE":        {"name": "Unemployment rate",                "category": "labor",      "frequency": "M", "units": "%",         "mart_column": "unemployment",         "cycle_lens": "deflationary"},
    "UMCSENT":       {"name": "Consumer sentiment (U. Michigan)", "category": "sentiment",  "frequency": "M", "units": "index",     "mart_column": "consumer_sentiment",   "cycle_lens": "both", "staleness_days": 100},
    "USREC":         {"name": "NBER recession indicator",         "category": "cycle",      "frequency": "M", "units": "0/1",       "mart_column": "recession",            "cycle_lens": "both"},
    "A191RL1Q225SBEA": {"name": "Real GDP growth (annualized)",   "category": "growth",     "frequency": "Q", "units": "%",         "mart_column": "gdp_growth",           "cycle_lens": "both"},
    "SP500":         {"name": "S&P 500 index",                    "category": "markets",    "frequency": "D", "units": "index",     "mart_column": "sp500",                "cycle_lens": "deflationary"},
    "CSUSHPINSA":    {"name": "Case-Shiller national home price index", "category": "housing", "frequency": "M", "units": "index",  "mart_column": "home_price_index",     "cycle_lens": "deflationary", "staleness_days": 100},
    "DTWEXBGS":      {"name": "Trade-weighted dollar index",      "category": "markets",    "frequency": "D", "units": "index",     "mart_column": "dollar_index",         "cycle_lens": "inflationary"},
}

# Microeconomic drill-down: unemployment rate by state, FRED id pattern {code}UR.
STATE_CODES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY",
]
STATE_SERIES = {
    f"{code}UR": {"name": f"Unemployment rate, {code}", "category": "labor", "frequency": "M", "units": "%", "state": code, "cycle_lens": "deflationary"}
    for code in STATE_CODES
}

ALL_SERIES = {**NATIONAL_SERIES, **STATE_SERIES}

# Data-quality gate configuration.
# Plausible value bounds per category; observations outside are warnings.
RANGE_BOUNDS = {
    "rates":     (-5, 25),
    "labor":     (0, 35),
    "credit":    (0, 20000),
    "debt":      (0, 200),
    "prices":    (0, 500),
    "money":     (0, 30000),
    "sentiment": (0, 150),
    "cycle":     (0, 1),
    "growth":    (-35, 40),
    "markets":   (0, 50000),
    "housing":   (0, 500),
}
# Max acceptable days since the latest observation, by native frequency.
STALENESS_DAYS = {"D": 14, "W": 21, "M": 75, "Q": 190}
# Series that feed the composite cycle-pressure score (z-scores averaged).
PRESSURE_COMPONENTS = ["household_debt_gdp", "debt_service_ratio", "cc_delinquency", "fedfunds"]
Z_WINDOW_MONTHS = 120
