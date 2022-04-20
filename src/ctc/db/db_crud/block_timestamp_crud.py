from __future__ import annotations

import typing

from typing_extensions import Literal
import toolsql

from ctc import spec
from .. import schema_utils


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
    blocks_timestamps: typing.Mapping[int, int],
    network: spec.NetworkReference | None = None,
) -> None:

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


def get_timestamp_block(
    conn: toolsql.SAConnection,
    timestamp: int,
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> int | None:
    """

    possible approaches to ensure db has enough data to give answer:
    - possibilities
        - run two queries, like (gte + lt) or (lte + gt)
            - limit = 1 on both
            - make sure that the results are only one apart
        - run one query first, then...
            - run second query to make sure result+1 or result-1 is in db
        - assume db is complete, do not perform additional checks
    - the relative speeds of these operations matter
        - this all could be bikeshedding
    """

    table = schema_utils.get_table_name('block_timestamps', network=network)

    if mode == 'before':
        query = {'where_lte': {'timestamp': timestamp}}
    elif mode == 'after':
        query = {'where_gte': {'timestamp': timestamp}}
    elif mode == 'equal':
        query = {'where_equals': {'timestamp': timestamp}}
    else:
        raise Exception('unknown mode: ' + str(mode))

    block_number = toolsql.select(
        conn=conn,
        table=table,
        return_count='one',
        only_columns=['block_number'],
        row_format='only_column',
        **query,
    )

    if block_number is not None:
        if mode == 'before':
            # assert block after is in db
            next_timestamp = get_block_timestamp(
                conn=conn,
                block_number=block_number + 1,
            )
            if next_timestamp is None:
                return None
        elif mode == 'after':
            # assert block before is in db
            previous_timestamp = get_block_timestamp(
                conn=conn,
                block_number=block_number - 1,
            )
            # raise Exception()
            if previous_timestamp is None:
                return None

    return block_number


def get_block_timestamp(
    conn: toolsql.SAConnection,
    block_number: int,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    return toolsql.select(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        row_format='only_column',
        only_columns=['timestamp'],
        return_count='one',
    )


def get_max_block_number(
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int:
    table = schema_utils.get_table_name('block_timestamps', network=network)
    result = toolsql.select(
        conn=conn,
        table=table,
        sql_functions=[
            ['max', 'block_number'],
        ],
        return_count='one',
    )
    return result['max__block_number']


def get_max_block_timestamp(
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int:
    table = schema_utils.get_table_name('block_timestamps', network=network)
    result = toolsql.select(
        conn=conn,
        table=table,
        sql_functions=[
            ['max', 'timestamp'],
        ],
        return_count='one',
    )
    return result['max__timestamp']


def get_timestamps_blocks(
    conn: toolsql.SAConnection,
    timestamps: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> list[int | None]:
    return [
        get_timestamp_block(
            conn=conn,
            timestamp=timestamp,
            network=network,
            mode=mode,
        )
        for timestamp in timestamps
    ]


def get_blocks_timestamps(
    conn: toolsql.SAConnection,
    block_numbers: typing.Sequence[typing.SupportsInt],
    network: spec.NetworkReference | None = None,
) -> list[int | None]:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    block_numbers_int = [int(item) for item in block_numbers]

    results = toolsql.select(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers_int},
    )

    blocks_timestamps = {
        row['block_number']: row['timestamp'] for row in results
    }

    return [
        blocks_timestamps.get(block_number) for block_number in block_numbers
    ]


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

