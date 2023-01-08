from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_block_transaction_query(
    block_number: int,
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_name(
        'block_transaction_queries',
        context=context,
    )
    toolsql.insert(
        conn=conn,
        table=table,
        row={'block_number': block_number},
        upsert='do_update',
    )


async def async_upsert_block_transaction_queries(
    block_numbers: typing.Sequence[int],
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> None:

    if len(block_numbers) == 0:
        return

    table = schema_utils.get_table_name(
        'block_transaction_queries',
        context=context,
    )
    rows = [{'block_number': block_number} for block_number in block_numbers]
    toolsql.insert(
        conn=conn,
        table=table,
        rows=rows,
        upsert='do_update',
    )


async def async_select_block_transaction_queries(
    *,
    block_numbers: typing.Sequence[int] | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> typing.Mapping[int, bool] | None:

    table = schema_utils.get_table_name(
        'block_transaction_queries',
        context=context,
    )

    if block_numbers is not None:
        queries = toolsql.select(
            conn=conn,
            table=table,
            where_in={'block_number': block_numbers},
            raise_if_table_dne=True,
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
        queries = toolsql.select(
            conn=conn,
            table=table,
            where_lte=where_lte,
            where_gte=where_gte,
            raise_if_table_dne=True,
        )

    if queries is None:
        return None

    # process queries
    output = {query: True for query in queries}
    query_set = set(queries)

    if start_block is not None and end_block is not None:
        block_numbers = range(start_block, end_block + 1)
    if block_numbers is not None:
        for block_number in block_numbers:
            if block_number not in query_set:
                output[block_number] = False

    return output


async def async_select_block_transaction_query(
    block_number: int,
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> bool | None:
    """return True if transaction query exists for given block number"""

    table = schema_utils.get_table_name(
        'block_transaction_queries',
        context=context,
    )

    result = toolsql.select(
        conn=conn,
        table=table,
        where_in={'block_number': block_number},
        return_count='one',
        raise_if_table_dne=True,
    )

    return result is not None


async def async_delete_block_transaction_query(
    block_number: int,
    *,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:

    table = schema_utils.get_table_name(
        'block_transaction_queries', context=context
    )

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
    )


async def async_delete_block_transaction_queries(
    block_numbers: typing.Sequence[int],
    *,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:

    if len(block_numbers) == 0:
        return

    table = schema_utils.get_table_name(
        'block_transaction_queries', context=context
    )

    toolsql.delete(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
    )

