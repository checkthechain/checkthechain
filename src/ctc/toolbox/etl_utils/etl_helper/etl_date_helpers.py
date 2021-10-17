import numpy as np
import pandas as pd

from ctc.toolbox import etl_utils


def create_block_timestamp_column(df, block_timestamps=None):

    if block_timestamps is None:
        block_timestamps = etl_utils.load_block_timestamps()

    index = df.index

    if isinstance(index, pd.MultiIndex):
        # keep only first level of multiindex
        n_levels = len(df.index.names)
        df = df.droplevel(list(range(1, n_levels)))

    merged = pd.merge(
        df,
        pd.Series(block_timestamps, name='timestamp'),
        left_index=True,
        right_index=True,
        how='left',
    )
    merged.index = index

    return merged['timestamp']


def create_block_datetime_column(df, **kwargs):
    if 'timestamp' in df.columns:
        timestamp = df['timestamp']
    else:
        timestamp = create_block_timestamp_column(df, **kwargs)
    return pd.to_datetime(timestamp, unit='s')


def create_block_date_column(df, **kwargs):
    if 'datetime' in df.columns:
        datetime = df['datetime']
    else:
        datetime = create_block_timestamp_column(df, **kwargs)
    return datetime.dt.date


def create_block_week_column(df, **kwargs):
    if 'datetime' in df.columns:
        datetime = df['datetime']
    else:
        datetime = create_block_timestamp_column(df, **kwargs)
    year = datetime.dt.isocalendar().year.astype(str)
    week = datetime.dt.isocalendar().week.astype(str)
    return year + '-' + week


def add_missing_series_dates(series, datetimes, fill_value=0):
    series = series.copy()
    all_days = np.arange(
        datetimes.min().timestamp(),
        datetimes.max().timestamp(),
        86400,
    )
    for day in all_days:
        date = pd.to_datetime(day, unit='s').date()
        if date not in series:
            series[date] = fill_value
    series = series.sort_index()
    return series


def add_missing_series_weeks(series, datetimes, fill_value=0):

    series = series.copy()

    first_year = datetimes.dt.isocalendar().year.min()
    last_year = datetimes.dt.isocalendar().year.max()

    for year in range(first_year, last_year + 1):

        # get first week of year
        if year == first_year:
            first_week = datetimes.dt.isocalendar().week.min()
        else:
            first_week = 1

        # get last week of year
        if year == last_year:
            last_week = datetimes.dt.isocalendar().week.max()
        else:
            last_week = 52

        # iterate
        for week in list(range(first_week, last_week + 1)):
            week_str = str(year) + '-' + str(week)
            if week_str not in series:
                series[week_str] = fill_value

    series = series.sort_index()

    return series

