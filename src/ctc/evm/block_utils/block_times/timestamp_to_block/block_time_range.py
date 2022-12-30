from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


@typing.overload
async def async_resolve_block_range(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    allow_none: typing.Literal[False],
    context: spec.Context = None,
    to_int: typing.Literal[True],
    start_none_means: spec.BlockNumberReference | None = None,
    end_none_means: spec.BlockNumberReference | None = None,
) -> tuple[int, int]:
    ...


@typing.overload
async def async_resolve_block_range(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    allow_none: typing.Literal[False],
    context: spec.Context = None,
    to_int: typing.Literal[False] = False,
    start_none_means: spec.BlockNumberReference | None = None,
    end_none_means: spec.BlockNumberReference | None = None,
) -> tuple[spec.BlockNumberReference, spec.BlockNumberReference]:
    ...


@typing.overload
async def async_resolve_block_range(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    allow_none: bool,
    context: spec.Context = None,
    to_int: typing.Literal[True],
    start_none_means: spec.BlockNumberReference | None = None,
    end_none_means: spec.BlockNumberReference | None = None,
) -> tuple[int | None, int | None]:
    ...


@typing.overload
async def async_resolve_block_range(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    allow_none: bool,
    context: spec.Context = None,
    to_int: bool = False,
    start_none_means: spec.BlockNumberReference | None = None,
    end_none_means: spec.BlockNumberReference | None = None,
) -> tuple[spec.BlockNumberReference | None, spec.BlockNumberReference | None]:
    ...


async def async_resolve_block_range(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    allow_none: bool,
    context: spec.Context = None,
    to_int: bool = False,
    start_none_means: spec.BlockNumberReference | None = None,
    end_none_means: spec.BlockNumberReference | None = None,
) -> tuple[spec.BlockNumberReference | None, spec.BlockNumberReference | None]:
    """resolve block or timestamp range to a block range"""

    import asyncio

    if start_block is None and start_time is None:
        start_block = start_none_means
    if end_block is None and end_time is None:
        end_block = end_none_means

    tasks = {}
    if start_block is not None:
        if to_int:
            tasks['start_block'] = asyncio.create_task(
                evm.async_block_number_to_int(start_block, context=context)
            )
        else:
            start_block = start_block
    elif start_time is not None:
        tasks['start_block'] = asyncio.create_task(
            evm.async_get_block_of_timestamp(start_time, context=context)
        )
    else:
        if allow_none:
            start_block = None
        else:
            raise Exception('must specify start_block or start_time')

    if end_block is not None:
        if to_int:
            tasks['end_block'] = asyncio.create_task(
                evm.async_block_number_to_int(end_block, context=context)
            )
        else:
            end_block = end_block
    elif end_time is not None:
        tasks['end_block'] = asyncio.create_task(
            evm.async_get_block_of_timestamp(end_time, context=context)
        )
    else:
        if allow_none:
            end_block = None
        else:
            raise Exception('must specify end_block or end_time')

    if 'start_block' in tasks:
        start_block = await tasks['start_block']
    if 'end_block' in tasks:
        end_block = await tasks['end_block']

    return start_block, end_block
