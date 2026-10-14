import pandas as pd

from epo.data import hours_per_day, to_hourly

TZ = "Europe/Brussels"


def test_quarter_hours_are_averaged_to_hours():
    """Check that four quarter-hours become one hourly value: (10 + 20 + 30 + 60) / 4 = 30."""
    idx = pd.date_range("2025-10-05 10:00", periods=8, freq="15min", tz=TZ)
    df = pd.DataFrame({"p": [10, 20, 30, 60, 1, 1, 1, 1]}, index=idx)
    assert to_hourly(df)["p"].tolist() == [30.0, 1.0]


def test_incomplete_hour_becomes_nan():
    """Check that an hour with a missing quarter-hour is NaN, not a mean over three values."""
    idx = pd.date_range("2025-10-05 10:00", periods=8, freq="15min", tz=TZ).delete(5)
    df = pd.DataFrame({"p": range(len(idx))}, index=idx)
    assert to_hourly(df)["p"].isna().tolist() == [False, True]


def test_clock_change_days_have_25_and_23_hours():
    """Check the local day has 25 hours when the clock goes back and 23 when it goes forward."""
    autumn = pd.date_range("2025-10-26", "2025-10-27", freq="h", tz=TZ, inclusive="left")
    spring = pd.date_range("2026-03-29", "2026-03-30", freq="h", tz=TZ, inclusive="left")
    assert hours_per_day(pd.DataFrame(index=autumn)).iloc[0] == 25
    assert hours_per_day(pd.DataFrame(index=spring)).iloc[0] == 23