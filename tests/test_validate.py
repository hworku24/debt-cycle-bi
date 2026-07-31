"""Tests for the data-quality gate.

These cover the checks that actually caught something during the first live
run, plus the ones whose failure would let bad numbers through silently.
"""

import pandas as pd
import pytest

from etl.validate import check_series


def frame(dates, values):
    """Build the shape check_series expects: raw date/value columns plus the
    parsed obs_date, which is what load_series produces."""
    df = pd.DataFrame({"date": dates, "value": values})
    df["obs_date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def months(start, n):
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(start, periods=n, freq="MS")]


def codes(issues):
    return {i.check for i in issues}


def test_clean_series_passes():
    recent = pd.Timestamp.now().normalize() - pd.DateOffset(months=23)
    df = frame(months(recent, 24), [4.0] * 24)
    assert check_series("FEDFUNDS", df) == []


def test_duplicate_dates_are_critical():
    dates = months("2020-01-01", 6)
    dates[3] = dates[2]
    issues = check_series("FEDFUNDS", frame(dates, [4.0] * 6))
    assert "duplicate_dates" in codes(issues)
    assert any(i.severity == "critical" for i in issues if i.check == "duplicate_dates")


def test_unparseable_dates_are_critical():
    issues = check_series("FEDFUNDS", frame(["2020-01-01", "not-a-date"], [4.0, 4.1]))
    assert codes(issues) == {"date_parse"}
    assert issues[0].severity == "critical"


def test_missing_columns_are_critical():
    issues = check_series("FEDFUNDS", pd.DataFrame({"foo": [1]}))
    assert codes(issues) == {"schema"}


def test_out_of_range_values_warn():
    # FEDFUNDS is in the rates category, bounded to -5..25 in config.
    issues = check_series("FEDFUNDS", frame(months("2020-01-01", 3), [4.0, 4.1, 900.0]))
    range_issues = [i for i in issues if i.check == "range"]
    assert range_issues and range_issues[0].severity == "warning"


def test_gap_mid_series_warns_on_continuity():
    dates = months("2020-01-01", 12)
    del dates[5]
    issues = check_series("FEDFUNDS", frame(dates, [4.0] * 11))
    assert "continuity" in codes(issues)


def test_leading_gap_is_not_a_missing_value_failure():
    """TDSP has no data before 2005 and FRED pads the request with '.' markers.
    Those leading blanks are the series not existing yet, not a quality problem.
    """
    dates = months("2000-01-01", 120)
    values = [None] * 60 + [10.0] * 60
    issues = check_series("TDSP", frame(dates, values))
    assert "missing_values" not in codes(issues)


def test_stale_series_warns():
    old = pd.Timestamp("2015-01-01")
    issues = check_series("FEDFUNDS", frame(months(old, 12), [4.0] * 12))
    stale = [i for i in issues if i.check == "staleness"]
    assert stale and stale[0].severity == "warning"


@pytest.mark.parametrize("series_id", ["FEDFUNDS", "UNRATE", "CPIAUCSL"])
def test_bounds_exist_for_configured_series(series_id):
    """Every series needs range bounds for its category, otherwise the range
    check raises a KeyError at runtime instead of reporting."""
    df = frame(months(pd.Timestamp.now().normalize() - pd.DateOffset(months=5), 6), [1.0] * 6)
    check_series(series_id, df)
