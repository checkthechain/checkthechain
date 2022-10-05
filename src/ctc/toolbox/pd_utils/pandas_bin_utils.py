from __future__ import annotations

import typing

import pandas as pd

from ctc import spec


def bin_data(
    data: spec.Series | spec.DataFrame,
    bin_edges: typing.Sequence[int | float],
    f: str,
    labels: typing.Sequence[str] | None = None,
) -> typing.Any:

    if len(data.index.levels) == 1:  # type: ignore
        index = data.index
    else:
        index = data.index.get_level_values('block_number')

    if labels is not None and len(labels) == len(bin_edges):
        labels = labels[:-1]

    cuts = pd.cut(index, bins=bin_edges, labels=labels)
    groups = data.groupby(cuts)

    if f == 'groupby':
        return groups
    elif f == 'sum':
        return groups.sum()
    elif f == 'min':
        return groups.min()
    elif f == 'max':
        return groups.max()
    elif f == 'count':
        return groups.count()
    elif f == 'mean':
        return groups.mean()
    else:
        raise Exception('unknown function: ' + str(f))
