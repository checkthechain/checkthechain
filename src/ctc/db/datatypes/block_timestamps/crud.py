from __future__ import annotations

import typing

from typing_extensions import Literal

from ctc import spec

import toolsql
import tooltime
from ... import schema_utils


def get_block_of_timestamp(
    conn: toolsql.SAConnection,
    timestamp: tooltime.Timestamp,
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> int:

    table = schema_utils.get_network_table_name(
        table_name='block_timestamps',
        network=network,
    )

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
        row_format='dict',
        return_count='one',
        only_columns=['block_number'],
        **query,
    )


def get_timestamp_of_block(
    conn: toolsql.SAConnection,
    block: int,
    network: spec.NetworkReference,
) -> int:

    table = schema_utils.get_network_table_name(
        table_name='block_timestamps',
        network=network,
    )

    return toolsql.select(
        conn=conn,
        table=table,
        where_equal={'block_number': block},
        only_columns=['block_timestamp'],
    )


def get_blocks_of_timestamps(
    conn: toolsql.SAConnection,
    timestamps: tooltime.Timestamp,
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> list[int]:
    return [
        get_block_of_timestamp(
            conn=conn,
            timestamp=timestamp,
            network=network,
            mode=mode,
        )
        for timestamp in timestamps
    ]


def get_timestamps_of_blocks(
    conn: toolsql.SAConnection,
    blocks: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
) -> list[int]:

    table = schema_utils.get_network_table_name(
        table_name='block_timestamps',
        network=network,
    )

    return toolsql.select(
        conn=conn,
        table=table,
        where_in={'block_number': blocks},
        only_columns=['block_timestamp'],
    )

