from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ctc.db import schema_utils
from . import table_block_transaction_queries


async def async_select_block_transactions(
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> typing.Sequence[spec.DBTransaction] | None:
    result = await async_select_blocks_transactions(
        block_numbers=[block_number],
        conn=conn,
        context=context,
    )
    if result is None:
        return None
    transactions, manifest = result
    if len(manifest) > 0:
        return transactions
    else:
        return None


async def async_select_blocks_transactions(
    *,
    block_numbers: typing.Sequence[int] | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> tuple[typing.Sequence[spec.DBTransaction], typing.Sequence[int]] | None:

    blocks_present = await table_block_transaction_queries.async_select_block_transaction_queries(
        block_numbers=block_numbers,
        start_block=start_block,
        end_block=end_block,
        conn=conn,
        context=context,
    )
    if blocks_present is None or len(blocks_present) == 0:
        return None

    table = schema_utils.get_table_schema('transactions', context=context)
    columns = [
        column['name']
        for column in table['columns']
        if column['name'] != 'access_list'
    ]

    if block_numbers is not None:
        transactions: typing.Sequence[
            spec.DBTransaction
        ] = await toolsql.async_select(  # type: ignore
            conn=conn,
            table=table,
            where_in={'block_number': blocks_present},
            columns=columns,
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
        transactions = await toolsql.async_select(  # type: ignore
            conn=conn,
            table=table,
            where_lte=where_lte,
            where_gte=where_gte,
            columns=columns,
        )

    return transactions, blocks_present

