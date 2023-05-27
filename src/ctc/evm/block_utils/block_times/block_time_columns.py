from __future__ import annotations

import typing

import ctc
from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_compute_column_block_month(
    block_number_series: spec.Series,
) -> spec.Series:
    return await async_compute_column_block_interval(
        block_number_series,
        interval_size='1M',
    )


async def async_compute_column_block_year(
    block_number_series,
) -> spec.Series:
    return await async_compute_column_block_interval(
        block_number_series,
        interval_size='1y',
    )


async def async_compute_column_block_week(
    block_number_series,
) -> spec.Series:
    return await async_compute_column_block_interval(
        block_number_series,
        interval_size='1w',
    )


async def async_compute_column_block_day(
    block_number_series,
) -> spec.Series:
    return await async_compute_column_block_interval(
        block_number_series,
        interval_size='1d',
    )


async def async_compute_column_block_hour(
    block_number_series,
) -> spec.Series:
    return await async_compute_column_block_interval(
        block_number_series,
        interval_size='1h',
    )


async def async_compute_column_block_minute(
    block_number_series,
) -> spec.Series:
    return await async_compute_column_block_interval(
        block_number_series,
        interval_size='1m',
    )


async def async_compute_column_block_interval(
    block_number_series,
    interval_size: tooltime.Timelength | None = None,
    alias: str | None = None,
    context: spec.Context = None,
) -> spec.Series:
    block_intervals = await ctc.async_get_block_intervals(
        start_block=block_number_series.min(),
        end_block=block_number_series.max(),
        interval_size=interval_size,
        blocks_at='start',
        context={'cache': False},
    )
    return compute_column_block_time_interval(
        block_number_series,
        block_intervals=block_intervals,
        alias=alias,
    )


def compute_column_block_time_interval(
    block_number_series,
    block_intervals: spec.DataFrame,
    *,
    alias: str | None = None,
) -> spec.Series:
    import polars as pl

    if block_intervals is None:
        raise Exception('must specify block_intervals')
    if alias is None:
        alias = _compute_block_intervals_alias(block_intervals)

    return (
        block_number_series.cut(
            bins=block_intervals['block'][1:],
            labels=block_intervals['label'],
        )['category']
        .cast(pl.Utf8)
        .alias(alias)
    )


def _compute_block_intervals_alias(block_intervals) -> spec.Series:
    timestamps = block_intervals['start_timestamp']
    interval_sizes = set(timestamps[1:] - timestamps[:-1])

    if interval_sizes.issubset({365 * 86400, 366 * 86400}):
        return 'year'
    if interval_sizes.issubset(
        {28 * 86400, 29 * 86400, 30 * 86400, 31 * 86400}
    ):
        return 'month'
    elif interval_sizes.issubset({86400 * 7}):
        return 'week'
    elif interval_sizes.issubset({86400}):
        return 'day'
    elif interval_sizes.issubset({3600}):
        return 'hour'
    elif interval_sizes.issubset({60}):
        return 'minute'
    elif interval_sizes.issubset({1}):
        return 'second'
    else:
        raise Exception('unknown label for interval')

