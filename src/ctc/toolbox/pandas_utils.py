import typing

from ctc import spec
import numpy as np
import pandas as pd


def create_timestamp_column(
    df: spec.DataFrame,
    timestamps: typing.Sequence[int],
) -> spec.Series:
    """create a timestamp column series that shares an index with dataframe"""

    index = df.index

    if isinstance(index, pd.MultiIndex):
        # keep only first level of multiindex
        n_levels = len(df.index.names)
        df = typing.cast(spec.DataFrame, df.droplevel(list(range(1, n_levels))))

    merged = pd.merge(
        df,
        pd.Series(timestamps, name='timestamp'),
        left_index=True,
        right_index=True,
        how='left',
    )
    merged.index = index

    return merged['timestamp']


def create_datetime_column(df: spec.DataFrame, timestamps=None) -> spec.Series:
    if 'timestamp' in df.columns:
        timestamp_column = df['timestamp']
    else:
        if timestamps is None:
            raise Exception('must specify timestamps')
        timestamp_column = create_timestamp_column(df, timestamps)
    return pd.to_datetime(timestamp_column, unit='s')


def create_date_column(df, timestamps=None):
    if 'datetime' in df.columns:
        datetime = df['datetime']
    else:
        if timestamps is None:
            raise Exception('must specify timestamps')
        datetime = create_timestamp_column(df, timestamps)
    return datetime.dt.date


def create_week_column(df: spec.DataFrame, timestamps: typing.Sequence[int]):
    if 'datetime' in df.columns:
        datetime = df['datetime']
    else:
        datetime = create_timestamp_column(df, timestamps)
    year = datetime.dt.isocalendar().year.astype(str)
    week = datetime.dt.isocalendar().week.astype(str)
    return year + '-' + week


def add_missing_series_dates(
        series: spec.Series, datetimes: spec.Series, fill_value: int = 0
) -> spec.Series:
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


def add_missing_series_weeks(
    series: spec.Series, datetimes: spec.Series, fill_value: int = 0
) -> spec.Series:

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

