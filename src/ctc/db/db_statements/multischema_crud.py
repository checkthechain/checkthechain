from __future__ import annotations

import asyncio
import typing
from typing_extensions import Literal

import toolsql

from ctc import spec
from .. import db_management
from .. import db_schemas


async def async_select_timestamp_block(
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

    if mode == 'before':
        query = {
            'where_lte': {'timestamp': timestamp},
            'order_by': {'column': 'block_number', 'order': 'descending'},
        }
    elif mode == 'after':
        query = {'where_gte': {'timestamp': timestamp}}
    elif mode == 'equal':
        query = {'where_equals': {'timestamp': timestamp}}
    else:
        raise Exception('unknown mode: ' + str(mode))

    timestamp_schema = db_management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        table = db_schemas.get_table_name('block_timestamps', network=network)
        block_number = toolsql.select(
            conn=conn,
            table=table,
            return_count='one',
            only_columns=['block_number'],
            row_format='only_column',
            **query,
        )
    elif timestamp_schema == 'blocks':
        raise NotImplementedError()
    else:
        return None

    if block_number is not None:
        if mode == 'before':
            # assert block after is in db
            next_timestamp = await async_select_block_timestamp(
                conn=conn,
                block_number=block_number + 1,
            )
            if next_timestamp is None:
                return None
        elif mode == 'after':
            # assert block before is in db
            previous_timestamp = await async_select_block_timestamp(
                conn=conn,
                block_number=block_number - 1,
            )
            if previous_timestamp is None:
                return None

    return block_number


async def async_select_block_timestamp(
    conn: toolsql.SAConnection,
    block_number: int,
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = db_management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        table = db_schemas.get_table_name('block_timestamps', network=network)

        return toolsql.select(
            conn=conn,
            table=table,
            where_equals={'block_number': block_number},
            row_format='only_column',
            only_columns=['timestamp'],
            return_count='one',
        )

    elif timestamp_schema == 'blocks':
        raise NotImplementedError()

    else:
        return None


async def async_select_max_block_number(
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = db_management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        table = db_schemas.get_table_name('block_timestamps', network=network)
        result = toolsql.select(
            conn=conn,
            table=table,
            sql_functions=[
                ['max', 'block_number'],
            ],
            return_count='one',
        )
        return result['max__block_number']

    elif timestamp_schema == 'blocks':
        raise NotImplementedError()

    else:
        return None


async def async_select_max_block_timestamp(
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:
    timestamp_schema = db_management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        table = db_schemas.get_table_name('block_timestamps', network=network)
        result = toolsql.select(
            conn=conn,
            table=table,
            sql_functions=[
                ['max', 'timestamp'],
            ],
            return_count='one',
        )
        return result['max__timestamp']

    elif timestamp_schema == 'blocks':
        raise NotImplementedError()

    else:
        return None


async def async_select_timestamps_blocks(
    conn: toolsql.SAConnection,
    timestamps: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> list[int | None]:

    timestamp_schema = db_management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        coroutines = [
            async_select_timestamp_block(
                conn=conn,
                timestamp=timestamp,
                network=network,
                mode=mode,
            )
            for timestamp in timestamps
        ]
        return await asyncio.gather(*coroutines)

    elif timestamp_schema == 'blocks':
        raise NotImplementedError()

    else:
        return [None] * len(timestamps)


async def async_select_block_timestamps(
    conn: toolsql.SAConnection,
    block_numbers: typing.Sequence[typing.SupportsInt],
    network: spec.NetworkReference | None = None,
) -> list[int | None]:

    timestamp_schema = db_management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        table = db_schemas.get_table_name('block_timestamps', network=network)

        block_numbers_int = [int(item) for item in block_numbers]

        results = toolsql.select(
            conn=conn,
            table=table,
            where_in={'block_number': block_numbers_int},
        )

        block_timestamps = {
            row['block_number']: row['timestamp'] for row in results
        }

        return [
            block_timestamps.get(block_number) for block_number in block_numbers
        ]

    elif timestamp_schema == 'blocks':
        raise NotImplementedError()

    else:
        return [None] * len(block_numbers)
