from __future__ import annotations

import typing

import pandas as pd

from ctc import spec


def create_empty_dataframe(
    column_names: typing.Sequence[str],
    *,
    index_names: typing.Sequence[str] | None = None,
    column_types: typing.Mapping[str, typing.Any] | None = None,
) -> spec.DataFrame:
    """create empty dataframe with specified metadata"""

    if index_names is not None:
        df = pd.DataFrame(columns=tuple(column_names) + tuple(index_names))  # type: ignore
        df = df.set_index(index_names)
    else:
        df = pd.DataFrame(columns=column_names)  # type: ignore

    if column_types is not None:
        raise NotImplementedError()

    if typing.TYPE_CHECKING:
        return typing.cast(spec.DataFrame, df)
    else:
        return df

