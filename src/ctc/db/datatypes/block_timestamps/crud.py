from __future__ import annotations

import typing

from typing_extensions import Literal
import toolsql

from ctc import spec
from ... import schema_utils


def set_block_timestamp(
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


def set_blocks_timestamps(
    conn: toolsql.SAConnection,
    block_timestamps: typing.Mapping[int, int],
    network: spec.NetworkReference | None = None,
) -> None:

    rows = [
        {'block_number': block_number, 'timestamp': timestamp}
        for block_number, timestamp in block_timestamps.items()
    ]
    table = schema_utils.get_table_name('block_timestamps', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=rows,
        upsert='do_update',
    )


def get_timestamp_block(
    conn: toolsql.SAConnection,
    timestamp: int,
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> int:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    if mode == 'before':
        query = {'where_lte': timestamp}
    elif mode == 'after':
        query = {'where_gte': timestamp}
    elif mode == 'equal':
        query = {'where_gte': timestamp}
    else:
        raise Exception('unknown mode: ' + str(mode))

    return toolsql.select(
        conn=conn,
        table=table,
        return_count='one',
        only_columns=['block_number'],
        row_format='only_column',
        **query,
    )


def get_block_timestamp(
    conn: toolsql.SAConnection,
    block_number: int,
    network: spec.NetworkReference | None = None,
) -> int:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    return toolsql.select(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        row_format='only_column',
        only_columns=['timestamp'],
        return_count='one',
    )


def get_timestamps_blocks(
    conn: toolsql.SAConnection,
    timestamps: int,
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> list[int]:
    return [
        get_block_timestamp(
            conn=conn,
            timestamp=timestamp,
            network=network,
            mode=mode,
        )
        for timestamp in timestamps
    ]


def get_blocks_timestamps(
    conn: toolsql.SAConnection,
    block_numbers: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
) -> list[int]:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    return toolsql.select(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
        only_columns=['timestamp'],
        row_format='only_column',
    )


def delete_block_timestamp(
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


def delete_blocks_timestamps(
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

