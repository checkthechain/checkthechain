from __future__ import annotations

import typing

from ctc import spec


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
    import polars as pl

    # assemble data
    df = pl.DataFrame({'index': indices, 'value': values})
    if volumes is not None:
        df = df.with_columns(pl.Series('volume', volumes))

    # set bins
    if bins is None:
        if bin_size is None:
            raise Exception('must specify bins or bin_size')
        bins_float = np.floor(df['index'].to_numpy() / bin_size) * bin_size
        bins = bins_float.astype(int)
    else:
        bin_size = bins[1] - bins[0]  # type: ignore
    if bin_size is None:
        raise Exception('bin_size could not be determined')
    df = df.with_columns(pl.Series('bin', bins))

    # compute metrics
    df = df.groupby('bin').agg(
        pl.col('value').first().alias('open'),
        pl.col('value').max().alias('high'),
        pl.col('value').min().alias('low'),
        pl.col('value').last().alias('close'),
        pl.col('value').count().alias('count'),
    )
    if volumes is not None:
        df = df.with_columns(pl.col('volume').sum().alias('volume'))

    # fill in missing bins
    all_bins = np.arange(
        bins[0], bins[-1] + bin_size, bin_size
    )
    n_to_add = len(all_bins) - len(df)
    if n_to_add > 0:
        last_close = df['close'][-1]
        row = [last_close, None, None, last_close, 0]
        if volumes is not None:
            row.append(0)
        missing_rows = pl.DataFrame(row * n_to_add, schema=df.schema)
        df = pl.concat([df, missing_rows])

    df = df.sort('bin')

    return df

