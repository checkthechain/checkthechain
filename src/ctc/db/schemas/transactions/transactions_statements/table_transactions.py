from __future__ import annotations

import typing

import toolsql

from ctc import evm
from ctc import spec
from ... import schema_utils


async def async_upsert_transaction(
    db_transaction: spec.DBTransaction,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema('transactions', context=context)

    tx = evm.convert_db_transaction_fields_to_text(db_transaction)

    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=tx,
        upsert=True,
    )


async def async_upsert_transactions(
    transactions: typing.Sequence[spec.DBTransaction],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema('transactions', context=context)

    if len(transactions) == 0:
        return

    txs = [evm.convert_db_transaction_fields_to_text(tx) for tx in transactions]

    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=txs,
        upsert=True,
    )


async def async_select_transaction(
    hash: str,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> spec.DBTransaction | None:

    table = schema_utils.get_table_schema('transactions', context=context)

    columns = [
        column['name']
        for column in table['columns']
        if column['name'] != 'access_list'
    ]

    tx: spec.DBTransactionText | None = await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        columns=columns,
        where_equals={'hash': hash},
        output_format='single_dict_or_none',
    )

    if tx is None:
        return None
    else:
        return evm.convert_db_transaction_fields_to_int(tx)


async def async_select_transactions(
    hashes: typing.Sequence[str],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> typing.Sequence[spec.DBTransaction | None] | None:

    table = schema_utils.get_table_schema('transactions', context=context)

    columns = [
        column['name']
        for column in table['columns']
        if column['name'] != 'access_list'
    ]

    transactions: typing.Sequence[
        spec.DBTransaction
    ] = await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        columns=columns,
        where_in={'hash': hashes},
    )

    if transactions is None:
        return None

    result = {tx['hash']: tx for tx in transactions}

    return [result.get(tx_hash) for tx_hash in hashes]


async def async_delete_transaction(
    hash: str,
    *,
    context: spec.Context,
    conn: toolsql.AsyncConnection,
) -> None:

    table = schema_utils.get_table_schema('transactions', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'hash': hash},
    )


async def async_delete_transactions(
    hashes: typing.Sequence[str],
    *,
    context: spec.Context,
    conn: toolsql.AsyncConnection,
) -> None:

    if len(hashes) == 0:
        return

    table = schema_utils.get_table_schema('transactions', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_in={'hash': hashes},
    )

