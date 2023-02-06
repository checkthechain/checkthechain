from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import management
from . import block_timestamps_statements
from ..blocks import blocks_statements


async def async_select_block_timestamp(
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_block_timestamp(
            conn=conn,
            block_number=block_number,
            context=context,
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_block_timestamp(
            conn=conn,
            block_number=block_number,
            context=context,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> list[int | None] | None:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_block_timestamps(
            conn=conn,
            block_numbers=block_numbers,
            context=context,
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_block_timestamps(
            conn=conn,
            block_numbers=block_numbers,
            context=context,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_max_block_number(
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_max_block_number(
            conn=conn,
            context=context,
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_max_block_number(
            conn=conn,
            context=context,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_max_block_timestamp(
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:
    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return (
            await block_timestamps_statements.async_select_max_block_timestamp(
                conn=conn,
                context=context,
            )
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_max_block_timestamp(
            conn=conn,
            context=context,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))

