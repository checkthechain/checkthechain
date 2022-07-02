from __future__ import annotations

import typing

from ctc import spec

if typing.TYPE_CHECKING:
    import numpy


def compute_ohlc(
    values: typing.Sequence[spec.Number],
    indices: typing.Sequence[spec.Number],
    *,
    bin_size: spec.Number | None = None,
    bins: typing.Sequence[spec.Number] | None = None,
    volumes: typing.Sequence[spec.Number] | None = None,
) -> spec.DataFrame:
    # TODO: add full support for non-integer bins

    import numpy as np
    import pandas as pd

    # assemble data
    df = pd.DataFrame({'value': values}, index=indices)
    if volumes is not None:
        df['volume'] = volumes

    # set bins
    if bins is None:
        if bin_size is None:
            raise Exception('must specify bins or bin_size')
        bins_float = np.floor(df.index.values / bin_size) * bin_size
        bins = bins_float.astype(int)
    else:
        bin_size = bins[1] - bins[0]  # type: ignore
    if bin_size is None:
        raise Exception('bin_size could not be determined')
    df['bin'] = bins

    # compute metrics
    grouped_by_bin = df.groupby('bin')
    df = pd.DataFrame(
        {
            'open': grouped_by_bin['value'].first(),
            'high': grouped_by_bin['value'].max(),
            'low': grouped_by_bin['value'].min(),
            'close': grouped_by_bin['value'].last(),
            'count': grouped_by_bin['value'].count(),
        },
    )
    if volumes is not None:
        df['volume'] = grouped_by_bin['volume'].sum()

    # fill in missing bins
    all_bins: typing.Sequence['numpy.int64'] = np.arange(bins[0], bins[-1] + bin_size, bin_size)  # type: ignore
    missing_bins = [b for b in all_bins if b not in df.index]
    for missing_bin in missing_bins:
        previous_close = df.loc[missing_bin - bin_size]['close']
        row = [previous_close, np.nan, np.nan, previous_close, 0]
        if volumes is not None:
            row.append(0)
        df.loc[missing_bin] = row
    df = df.sort_index()

    return df
