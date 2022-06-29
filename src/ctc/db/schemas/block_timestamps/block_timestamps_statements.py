from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_block_timestamp(
    *,
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


async def async_upsert_block_timestamps(
    *,
    conn: toolsql.SAConnection,
    block_timestamps: typing.Mapping[int, int] | None = None,
    blocks: typing.Sequence[spec.Block] | None = None,
    network: spec.NetworkReference | None = None,
) -> None:

    if block_timestamps is None:
        if blocks is None:
            raise Exception('must specify block_timestamps or blocks')
        block_timestamps = {
            block['number']: block['timestamp'] for block in blocks
        }

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


async def async_delete_block_timestamp(
    *,
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


async def async_delete_block_timestamps(
    *,
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


#
# # do not export
#


async def async_select_block_timestamp(
    block_number: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    result = toolsql.select(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        row_format='only_column',
        only_columns=['timestamp'],
        return_count='one',
        raise_if_table_dne=False,
    )
    if result is not None and not isinstance(result, int):
        raise Exception('invalid db result')
    return result


async def async_select_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> list[int | None] | None:

    table = schema_utils.get_table_name('block_timestamps', network=network)

    block_numbers_int = [int(item) for item in block_numbers]

    results = toolsql.select(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers_int},
        raise_if_table_dne=False,
    )

    if results is None:
        return results

    block_timestamps = {
        row['block_number']: row['timestamp'] for row in results
    }

    return [
        block_timestamps.get(block_number) for block_number in block_numbers
    ]


async def async_select_max_block_number(
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('block_timestamps', network=network)
    result = toolsql.select(
        conn=conn,
        table=table,
        sql_functions=[
            ['max', 'block_number'],
        ],
        return_count='one',
        raise_if_table_dne=False,
    )
    if result is None:
        return None
    subresult = result['max__block_number']
    if subresult is not None and not isinstance(subresult, int):
        raise Exception('invalid db result')
    return subresult


async def async_select_max_block_timestamp(
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('block_timestamps', network=network)
    result = toolsql.select(
        conn=conn,
        table=table,
        sql_functions=[
            ['max', 'timestamp'],
        ],
        return_count='one',
        raise_if_table_dne=False,
    )
    if result is None:
        return None

    subresult = result['max__timestamp']
    if subresult is not None and not isinstance(subresult, int):
        raise Exception('invalid db result')
    return subresult


async def async_select_timestamp_block_range(
    timestamp: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> tuple[int | None, int | None]:
    """return block range that must contain timestamp

    this function is used to confine a block-of-timestamp search
    """

    table = schema_utils.get_table_name('block_timestamps', network=network)

    lower_bound = toolsql.select(
        conn=conn,
        table=table,
        where_lte={'timestamp': timestamp},
        sql_functions=[
            ['max', 'block_number'],
        ],
        return_count='one',
        raise_if_table_dne=False,
    )
    upper_bound = toolsql.select(
        conn=conn,
        table=table,
        where_gte={'timestamp': timestamp},
        sql_functions=[
            ['min', 'block_number'],
        ],
        return_count='one',
        raise_if_table_dne=False,
    )

    return lower_bound['max__block_number'], upper_bound['min__block_number']


__all__ = (
    'async_upsert_block_timestamp',
    'async_upsert_block_timestamps',
    'async_delete_block_timestamp',
    'async_delete_block_timestamps',
)
