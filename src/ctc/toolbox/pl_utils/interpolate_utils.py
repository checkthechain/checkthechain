from __future__ import annotations

import typing

import polars as pl
from ctc.toolbox import pl_utils


def interpolate(
    df: pl.DataFrame,
    *,
    index_column: str,
    start_index: int | None = None,
    end_index: int | None = None,
    pre_fill_values: typing.Mapping[str, typing.Any] | None = None,
) -> pl.DataFrame:
    """interpolate values in dataframe according to index column"""

    index = df[index_column]

    # validate index
    if index.dtype not in [pl.Int8, pl.Int16, pl.Int32, pl.Int64]:
        raise Exception('index must be an integer column')
    if not index.series_equal(index.sort()):
        raise Exception('index must be a sorted column')
    if start_index is not None:
        if start_index > index[0]:
            raise Exception('start_index is larger than first index in df')
    else:
        start_index = index[0]
    if end_index is not None:
        if end_index < index[-1]:
            raise Exception('end_index is smaller than last index in df')
    else:
        end_index = index[-1]

    # build new index and initial values
    if start_index < index[0]:
        if pre_fill_values is None:
            raise Exception('must specify pre_fill_values if start_index < index[0]')
        initial_values = {k: [v] for k, v in pre_fill_values.items()}
        initial_values[index_column] = [start_index]
        for column in df.columns:
            if column not in initial_values and column != index_column:
                initial_values[column] = None
        initial_df = pl.DataFrame(initial_values, schema=df.schema)
        new_index = range(start_index + 1, end_index + 1)
    else:
        initial_df = None
        new_index = range(start_index, end_index + 1)

    # create interpolation rows
    new_data = {column: None for column in df.columns if column != index_column}
    new_data[index_column] = (
        pl.DataFrame(pl.Series(index_column, new_index))
        .filter(~pl.col(index_column).is_in(df[index_column]))[index_column]
    )
    new_df = pl.DataFrame(new_data, schema=df.schema)

    # concat, sort, and fill
    if initial_df is not None:
        dfs = [initial_df, df, new_df]
    else:
        dfs = [df, new_df]
    return pl_utils.concat(dfs).sort(index_column).fill_null(strategy='forward')

