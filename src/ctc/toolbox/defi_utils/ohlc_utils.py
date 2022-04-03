from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    number = typing.SupportsInt | typing.SupportsFloat

from ctc import spec


def compute_ohlc(
    values: typing.Sequence[number],
    indices: typing.Sequence[number],
    bin_size: number | None = None,
    bins: typing.Sequence[number] | None = None,
    volumes: typing.Sequence[number] | None = None,
) -> spec.DataFrame:

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
        bins = np.floor(df.index.values / bin_size) * bin_size
        bins = bins.astype(int)
    else:
        bin_size = bins[1] - bins[0]
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
    all_bins = np.arange(bins[0], bins[-1] + bin_size, bin_size)
    missing_bins = [b for b in all_bins if b not in df.index]
    for missing_bin in missing_bins:
        previous_close = df.loc[missing_bin - bin_size]['close']
        row = [previous_close, np.nan, np.nan, previous_close, 0]
        if volumes is not None:
            row.append(0)
        df.loc[missing_bin] = row
    df = df.sort_index()

    return df

