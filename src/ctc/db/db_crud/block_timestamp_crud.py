from __future__ import annotations

import typing

import toolsql

from ctc import spec
from .. import schema_utils


async def async_store_block_timestamp(
    conn: toolsql.SAConnection,
    block_number: int,
    timestamp: int,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('block_timestamps', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row={'block_number': block_number, 'timestamp': timestamp},
        upsert='do_update',
    )


async def async_store_blocks_timestamps(
    conn: toolsql.SAConnection,
    blocks_timestamps: typing.Mapping[int, int] | None = None,
    blocks: typing.Sequence[spec.Block] | None = None,
    network: spec.NetworkReference | None = None,
) -> None:

    if blocks_timestamps is None:
        if blocks is None:
            raise Exception('must specify blocks_timestamps or blocks')
        blocks_timestamps = {
            block['number']: block['timestamp'] for block in blocks
        }

    rows = [
        {'block_number': block_number, 'timestamp': timestamp}
        for block_number, timestamp in blocks_timestamps.items()
    ]
    table = schema_utils.get_table_name('block_timestamps', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=rows,
        upsert='do_update',
    )


async def async_delete_block_timestamp(
    conn: toolsql.SAConnection,
    block_number: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
    )


async def async_delete_blocks_timestamps(
    conn: toolsql.SAConnection,
    block_numbers: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
    )
