from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from ctc import spec


def keep_level(index: pd.MultiIndex, level: str) -> pd.Index:
    """drop all levels in a multiindex except for one"""
    for other_level in list(index.names):
        if other_level != level:
            index = index.droplevel(other_level)
    return index


def interpolate_series(
    series: spec.Series,
    *,
    start_index: typing.Optional[int] = None,
    end_index: typing.Optional[int] = None,
    pre_fill_value: typing.Any = None,
    level: typing.Optional[str] = None,
) -> spec.Series:

    # drop extra levels
    old_index = series.index
    if isinstance(old_index, pd.MultiIndex):
        if level is None:
            raise Exception('must specify which index level to use')
        series = series.copy()
        series.index = keep_level(old_index, level)

    # remove duplicate index values, keeping last value of each duplicate
    series = series[~series.index.duplicated(keep='last')]

    # build new index
    if start_index is None:
        start_index = series.index.values[0]
    if end_index is None:
        end_index = series.index.values[-1]
    new_index: spec.NumpyArray = np.arange(
        start_index, end_index + 1, 1, dtype=int
    )

    # create new series
    new_series = typing.cast(
        pd.Series, series.reindex(new_index, fill_value=pd.NA)
    )

    # insert pre fill value
    if len(series) > 0:
        if start_index < series.index.values[0]:
            if pre_fill_value is None:
                raise Exception('for early start must specify pre_fill_value')
            new_series.iloc[0] = pre_fill_value
        elif start_index > series.index.values[-1]:
            # case: indicies start after the series ends
            new_series.iloc[0] = series.values[-1]
        elif start_index > series.index.values[0]:
            # fill in any initial values that were cut off
            fill_index = np.nonzero(series.index > start_index)[0][0] - 1  # type: ignore
            new_series.iloc[0] = series.iloc[fill_index]

    # interpolate values
    if len(series) == 0 and len(new_series) > 0 and pre_fill_value is not None:
        new_series.iloc[0] = pre_fill_value
    new_series = new_series.fillna(method='ffill')

    return new_series


def interpolate_dataframe(
    df: spec.DataFrame,
    *,
    start_index: typing.Optional[int] = None,
    end_index: typing.Optional[int] = None,
    level: typing.Optional[str] = None,
) -> spec.DataFrame:

    # drop extra levels
    old_index = df.index
    if isinstance(old_index, pd.MultiIndex):
        if level is None:
            raise Exception('must specify which index level to use')
        df = df.copy()
        df.index = keep_level(old_index, level)

    # remove duplicate index values, keeping last value of each duplicate
    df = df[~df.index.duplicated(keep='last')]

    # build new index
    if start_index is None:
        start_index = df.index.values[0]
    if end_index is None:
        end_index = df.index.values[-1]
    new_index: spec.NumpyArray = np.arange(
        start_index, end_index + 1, 1, dtype=int
    )

    # create new series
    new_df = df.reindex(new_index, fill_value=pd.NA)

    # fill in cut off values
    if start_index > df.index.values[0]:
        fill_index = np.nonzero(df.index > start_index)[0][0] - 1
        new_df.iloc[0] = df.iloc[fill_index]

    # interpolate values
    new_df = new_df.fillna(method='ffill')

    return new_df
