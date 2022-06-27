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
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_block_timestamp(
            conn=conn,
            block_number=block_number,
            network=network,
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_block_timestamp(
            conn=conn,
            block_number=block_number,
            network=network,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> list[int | None] | None:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_block_timestamps(
            conn=conn,
            block_numbers=block_numbers,
            network=network,
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_block_timestamps(
            conn=conn,
            block_numbers=block_numbers,
            network=network,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_max_block_number(
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_max_block_number(
            conn=conn,
            network=network,
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_max_block_number(
            conn=conn,
            network=network,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_max_block_timestamp(
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:
    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return (
            await block_timestamps_statements.async_select_max_block_timestamp(
                conn=conn,
                network=network,
            )
        )

    elif timestamp_schema == 'blocks':
        return await blocks_statements.async_select_max_block_timestamp(
            conn=conn,
            network=network,
        )

    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))
