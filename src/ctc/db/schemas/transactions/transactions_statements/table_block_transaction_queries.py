from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_block_transaction_query(
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema(
        'block_transaction_queries',
        context=context,
    )
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row={'block_number': block_number},
        upsert=True,
    )


async def async_upsert_block_transaction_queries(
    block_numbers: typing.Sequence[int],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    if len(block_numbers) == 0:
        return

    table = schema_utils.get_table_schema(
        'block_transaction_queries',
        context=context,
    )
    rows = [{'block_number': block_number} for block_number in block_numbers]
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=rows,
        upsert=True,
    )


async def async_select_block_transaction_queries(
    *,
    block_numbers: typing.Sequence[int] | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> typing.Sequence[int] | None:

    table = schema_utils.get_table_schema(
        'block_transaction_queries',
        context=context,
    )

    if block_numbers is not None:
        queries: typing.Sequence[int] = await toolsql.async_select(
            conn=conn,
            table=table,
            where_in={'block_number': block_numbers},
            columns=['block_number'],
            output_format='single_column',
        )

    else:
        if start_block is not None:
            where_gte = {'block_number': start_block}
        else:
            where_gte = None
        if end_block is not None:
            where_lte = {'block_number': end_block}
        else:
            where_lte = None
        queries = await toolsql.async_select(
            conn=conn,
            table=table,
            where_lte=where_lte,
            where_gte=where_gte,
            columns=['block_number'],
            output_format='single_column',
        )

    return queries


async def async_select_block_transaction_query(
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> bool | None:
    """return True if transaction query exists for given block number"""

    table = schema_utils.get_table_schema(
        'block_transaction_queries',
        context=context,
    )

    result = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        output_format='single_dict_or_none',
    )

    return result is not None


async def async_delete_block_transaction_query(
    block_number: int,
    *,
    context: spec.Context,
    conn: toolsql.AsyncConnection,
) -> None:

    table = schema_utils.get_table_schema(
        'block_transaction_queries', context=context
    )

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
    )


async def async_delete_block_transaction_queries(
    block_numbers: typing.Sequence[int],
    *,
    context: spec.Context,
    conn: toolsql.AsyncConnection,
) -> None:

    if len(block_numbers) == 0:
        return

    table = schema_utils.get_table_schema(
        'block_transaction_queries', context=context
    )

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
    )

