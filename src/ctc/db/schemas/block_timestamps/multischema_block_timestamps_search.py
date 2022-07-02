from __future__ import annotations

import asyncio
import typing
from typing_extensions import Literal

import toolsql

from ctc import spec
from ... import management
from ... import schema_utils
from . import block_timestamps_statements

from .multischema_block_timestamps_statements import (
    async_select_block_timestamp,
)


async def async_select_timestamp_block(
    timestamp: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
    mode: Literal['<=', '>=', '=='] = '>=',
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

    if mode == '<=':
        query = {
            'where_lte': {'timestamp': timestamp},
            'order_by': {'column': 'block_number', 'order': 'descending'},
        }
    elif mode == '>=':
        query = {'where_gte': {'timestamp': timestamp}}
    elif mode == '==':
        query = {'where_equals': {'timestamp': timestamp}}
    else:
        raise Exception('unknown mode: ' + str(mode))

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        table = schema_utils.get_table_name('block_timestamps', network=network)
        block_number: int = toolsql.select(
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
        raise Exception('unknown schema: ' + str(timestamp_schema))

    if block_number is not None:
        if mode == '==':
            pass
        elif mode == '<=':
            # assert block after is in db
            next_timestamp = await async_select_block_timestamp(
                conn=conn,
                block_number=block_number + 1,
            )
            if next_timestamp is None:
                return None
        elif mode == '>=':
            # assert block before is in db
            previous_timestamp = await async_select_block_timestamp(
                conn=conn,
                block_number=block_number - 1,
            )
            if previous_timestamp is None:
                return None
        else:
            raise Exception('unknown mode: ' + str(mode))

    return block_number


async def async_select_timestamps_blocks(
    timestamps: typing.Sequence[int],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
    mode: Literal['<=', '>=', '=='] = '>=',
) -> list[int | None]:

    timestamp_schema = management.get_active_timestamp_schema()

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
        raise Exception('unknown schema: ' + str(timestamp_schema))


async def async_select_timestamp_block_range(
    timestamp: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> tuple[int | None, int | None]:

    timestamp_schema = management.get_active_timestamp_schema()

    if timestamp_schema == 'block_timestamps':
        return await block_timestamps_statements.async_select_timestamp_block_range(
            timestamp=timestamp,
            conn=conn,
            network=network,
        )
    elif timestamp_schema == 'blocks':
        raise NotImplementedError()
    else:
        raise Exception('unknown schema: ' + str(timestamp_schema))
