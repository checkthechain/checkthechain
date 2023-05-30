from __future__ import annotations

import typing

import ctc
from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_compute_block_years(
    block_numbers: typing.Sequence[int] | spec.Series,
) -> spec.Series:
    return await async_compute_block_time_bins(
        block_numbers,
        interval_size='1y',
        alias='year',
    )


async def async_compute_block_months(
    block_numbers: typing.Sequence[int] | spec.Series,
) -> spec.Series:
    return await async_compute_block_time_bins(
        block_numbers,
        interval_size='1M',
        alias='month',
    )


async def async_compute_block_weeks(
    block_numbers: typing.Sequence[int] | spec.Series,
) -> spec.Series:
    return await async_compute_block_time_bins(
        block_numbers,
        interval_size='1w',
        alias='week',
    )


async def async_compute_block_days(
    block_numbers: typing.Sequence[int] | spec.Series,
) -> spec.Series:
    return await async_compute_block_time_bins(
        block_numbers,
        interval_size='1d',
        alias='day',
    )


async def async_compute_block_hours(
    block_numbers: typing.Sequence[int] | spec.Series,
) -> spec.Series:
    return await async_compute_block_time_bins(
        block_numbers,
        interval_size='1h',
        alias='hour',
    )


async def async_compute_block_minutes(
    block_numbers: typing.Sequence[int] | spec.Series,
) -> spec.Series:
    return await async_compute_block_time_bins(
        block_numbers,
        interval_size='1m',
        alias='minute',
    )


async def async_compute_block_time_bins(
    block_numbers: typing.Sequence[int] | spec.Series,
    interval_size: tooltime.Timelength,
    alias: str | None = None,
    context: spec.Context = None,
) -> spec.Series:
    block_intervals = await ctc.async_get_block_intervals(
        start_block=min(block_numbers),
        end_block=max(block_numbers),
        interval_size=interval_size,
        blocks_at='start',
        context={'cache': False},
    )
    return compute_block_time_bins(
        block_numbers,
        block_intervals=block_intervals,
        alias=alias,
    )


def compute_block_time_bins(
    block_numbers: typing.Sequence[int] | spec.Series,
    block_intervals: spec.DataFrame,
    *,
    alias: str | None = None,
) -> spec.Series:
    import polars as pl

    if not isinstance(block_numbers, pl.Series):
        block_numbers = pl.Series(block_numbers)
    if alias is None:
        alias = _compute_block_intervals_alias(block_intervals)
    if alias is None:
        raise Exception('could not determine name of time bin')

    return (
        block_numbers.cut(
            bins=list(block_intervals['block'][1:]),
            labels=list(block_intervals['label']),
        )['category']
        .cast(pl.Utf8)
        .alias(alias)
    )


def _compute_block_intervals_alias(
    block_intervals: spec.DataFrame,
) -> str:

    if len(block_intervals) < 2:
        return None

    timestamps = block_intervals['start_timestamp']
    interval_sizes = set(timestamps[1:] - timestamps[:-1])

    if interval_sizes.issubset({365 * 86400, 366 * 86400}):
        return 'year'
    elif interval_sizes.issubset(
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

