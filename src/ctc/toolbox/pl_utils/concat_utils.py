from __future__ import annotations

import typing

import polars as pl

from ctc import spec


def concat(
    dfs: typing.Sequence[spec.DataFrame],
    **kwargs: typing.Any,
) -> spec.DataFrame:
    """like pl.concat, with support for objects"""

    # find object columns
    object_columns = []
    non_object_columns = []
    for column, datatype in dfs[0].schema.items():
        if datatype == pl.Object:
            object_columns.append(column)
        else:
            non_object_columns.append(column)

    # build object columns
    object_series = []
    for object_column in object_columns:
        values = []
        for df in dfs:
            values.extend(df[object_column].to_list())
        series = pl.Series(object_column, values, dtype=pl.Object)
        object_series.append(series)

    # concat non-object columns
    without_objects = [df[non_object_columns] for df in dfs]
    concated = pl.concat(without_objects, **kwargs)
    return concated.with_columns(object_series)

