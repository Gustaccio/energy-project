"""Collect ENTSO-E market data for the Belgian zone, month by month."""
import os
from pathlib import Path

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from entsoe import EntsoePandasClient
from entsoe.exceptions import NoMatchingDataError

load_dotenv(find_dotenv(usecwd=True))  # reads .env (never versioned): exposes ENTSOE_API_KEY

ZONE = "BE"
TZ = "Europe/Brussels"
RAW_DIR = Path("data/raw")

# Names returned by entsoe-py -> project names (unit in the name)
RENAME = {
    "Forecasted Load": "load_fc_mw",
    "Actual Load": "load_actual_mw",
    "Solar": "solar_fc_mw",
    "Wind Onshore": "wind_onshore_fc_mw",
    "Wind Offshore": "wind_offshore_fc_mw",
}


def get_client() -> EntsoePandasClient:
    """Create the ENTSO-E API client from the token stored in the environment."""
    key = os.environ.get("ENTSOE_API_KEY")
    if not key:
        raise RuntimeError("ENTSOE_API_KEY is empty: copy .env.example to .env and paste your token.")
    return EntsoePandasClient(api_key=key)


def queries(client) -> dict:
    """List the datasets to download: folder name -> function (start, end) that fetches it."""
    return {
        "da_price": lambda s, e: client.query_day_ahead_prices(ZONE, start=s, end=e)
        .rename("da_price_eur_mwh"),
        "load_fc": lambda s, e: client.query_load_forecast(ZONE, start=s, end=e),
        "wind_solar_fc": lambda s, e: client.query_wind_and_solar_forecast(ZONE, start=s, end=e),
        "load_actual": lambda s, e: client.query_load(ZONE, start=s, end=e),
    }

def fetch_month(name: str, query, month: pd.Period) -> None:
    """Download one dataset for one month and save it as data/raw/<ZONE>/<name>/<month>.parquet.

    A closed month already on disk is skipped; the current month is always downloaded again.
    """
    path = RAW_DIR / ZONE / name / f"{month}.parquet"  # e.g. data/raw/BE/da_price/2025-10.parquet
    start = month.start_time.tz_localize(TZ)
    end = (month + 1).start_time.tz_localize(TZ)
    now = pd.Timestamp.now(tz=TZ)
    month_is_closed = end <= now
    if path.exists() and month_is_closed:
        return  # closed month already downloaded: nothing to do
    query_end = min(end, now.normalize() + pd.Timedelta(days=2))  # never beyond tomorrow
    try:
        df = query(start, query_end)
    except NoMatchingDataError:
        print(f"{name} {month}: no data")
        return
    if isinstance(df, pd.Series):  # depending on the query: Series or DataFrame
        df = df.to_frame()
    df = df[df.index < end]  # the API may include the end bound
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)


def fetch_all(first: str = "2023-01", last: str | None = None, client=None) -> None:
    """Download all datasets month by month, from `first` to `last` (default: current month)."""
    client = client or get_client()
    current = pd.Timestamp.now(tz=TZ).tz_localize(None).to_period("M")
    months = pd.period_range(first, last or current, freq="M")
    for name, query in queries(client).items():
        for month in months:
            fetch_month(name, query, month)

def load_raw(name: str) -> pd.DataFrame:
    """Read the monthly files of one dataset and join them, without duplicate timestamps."""
    frames = [pd.read_parquet(f) for f in sorted((RAW_DIR / ZONE / name).glob("*.parquet"))]
    df = pd.concat(frames).sort_index()
    return df[~df.index.duplicated(keep="last")]


def to_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Average a mixed series (60, then 15 min) into hourly values. An incomplete hour is NaN."""
    grouped = df.resample("h")
    hourly = grouped.mean()
    n_obs = grouped.count()  # number of values actually present in each hour
    expected = n_obs.groupby(n_obs.index.normalize()).transform("max")  # 1 or 4 depending on the day
    return hourly.where(n_obs >= expected)


def build_hourly_dataset() -> pd.DataFrame:
    """Build the hourly dataset: one column per variable, with the unit in the column name."""
    parts = [to_hourly(load_raw(n)) for n in ("da_price", "load_fc", "wind_solar_fc", "load_actual")]
    return pd.concat(parts, axis=1).rename(columns=RENAME).sort_index()


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize each column: first date, last date and number of missing hours in between."""
    full = pd.date_range(df.index.min(), df.index.max(), freq="h")  # the time zone is inherited from the index
    df = df.reindex(full)  # an hour absent from every series becomes a row of NaN

    def gaps(s: pd.Series) -> int:
        """Count the NaN between the first and the last valid value of one column."""
        return int(s.loc[s.first_valid_index():s.last_valid_index()].isna().sum())

    return pd.DataFrame({
        "first_date": df.apply(lambda s: s.first_valid_index()),
        "last_date": df.apply(lambda s: s.last_valid_index()),
        "missing_hours": df.apply(gaps),
    })


def hours_per_day(df: pd.DataFrame) -> pd.Series:
    """Count the hours in each local day: 24 normally, 23 or 25 on clock-change days."""
    return df.groupby(df.index.normalize()).size()