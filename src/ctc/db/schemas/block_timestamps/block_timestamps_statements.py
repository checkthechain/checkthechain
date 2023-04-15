from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_block_timestamp(
    *,
    conn: toolsql.AsyncConnection,
    block_number: int,
    timestamp: int,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row={'block_number': block_number, 'timestamp': timestamp},
        upsert=True,
    )


async def async_upsert_block_timestamps(
    *,
    conn: toolsql.AsyncConnection,
    block_timestamps: typing.Mapping[int, int] | None = None,
    blocks: typing.Sequence[spec.DBBlock] | None = None,
    context: spec.Context = None,
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
    table = schema_utils.get_table_schema('block_timestamps', context=context)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=rows,
        upsert=True,
    )


async def async_delete_block_timestamp(
    *,
    conn: toolsql.AsyncConnection,
    block_number: typing.Sequence[int],
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
    )


async def async_delete_block_timestamps(
    *,
    conn: toolsql.AsyncConnection,
    block_numbers: typing.Sequence[int],
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)

    await toolsql.async_delete(
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
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)

    result = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        columns=['timestamp'],
        output_format='cell_or_none',
    )
    if result is not None and not isinstance(result, int):
        raise Exception('invalid db result')
    return result


async def async_select_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> list[int | None] | None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)

    block_numbers_int = [int(item) for item in block_numbers]

    results = await toolsql.async_select(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers_int},
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
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)

    # try-catch because connectorx panics on empty rows
    try:
        result = await toolsql.async_select(
            conn=conn,
            table=table,
            columns=['MAX(block_number)'],
            output_format='cell_or_none',
        )
    except RuntimeError as e:
        if e.args == ('Cannot infer type from null for SQLite',):
            return None
        else:
            raise e

    if result is None:
        return None
    elif isinstance(result, int):
        return result
    else:
        raise Exception('invalid db result')


async def async_select_max_block_timestamp(
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    table = schema_utils.get_table_schema('block_timestamps', context=context)

    # try-catch because connectorx panics on empty rows
    try:
        result = await toolsql.async_select(
            conn=conn,
            table=table,
            columns=['MAX(timestamp)'],
            output_format='cell_or_none',
        )
    except RuntimeError as e:
        if e.args == ('Cannot infer type from null for SQLite',):
            return None
        else:
            raise e

    if result is None:
        return None
    elif isinstance(result, int):
        return result
    else:
        raise Exception('invalid db result')


async def async_select_timestamp_block_range(
    timestamp: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> tuple[int | None, int | None]:
    """return block range that must contain timestamp

    this function is used to confine a block-of-timestamp search
    """

    # convert numpy types to native python type
    if type(timestamp).__name__.startswith('int'):
        timestamp = int(timestamp)

    table = schema_utils.get_table_schema('block_timestamps', context=context)
    lower_bound = await toolsql.async_select(
        conn=conn,
        table=table,
        where_lte={'timestamp': timestamp},
        columns=['MAX(block_number)'],
        output_format='cell_or_none',
    )
    upper_bound = await toolsql.async_select(
        conn=conn,
        table=table,
        where_gte={'timestamp': timestamp},
        columns=['MIN(block_number)'],
        output_format='cell_or_none',
    )

    return lower_bound, upper_bound


__all__ = (
    'async_upsert_block_timestamp',
    'async_upsert_block_timestamps',
    'async_delete_block_timestamp',
    'async_delete_block_timestamps',
)
