from __future__ import annotations

import typing

import toolsql

from ctc import evm
from ctc import spec
from ... import schema_utils


async def async_upsert_transaction(
    db_transaction: spec.DBTransaction,
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_name('transactions', context=context)

    tx = evm.convert_db_transaction_fields_to_text(db_transaction)

    toolsql.insert(
        conn=conn,
        table=table,
        row=tx,
        upsert='do_update',
    )


async def async_upsert_transactions(
    transactions: typing.Sequence[spec.DBTransaction],
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_name('transactions', context=context)

    if len(transactions) == 0:
        return

    txs = [evm.convert_db_transaction_fields_to_text(tx) for tx in transactions]

    toolsql.insert(
        conn=conn,
        table=table,
        rows=txs,
        upsert='do_update',
    )


async def async_select_transaction(
    hash: str,
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> spec.DBTransaction | None:

    table = schema_utils.get_table_name('transactions', context=context)

    tx: spec.DBTransactionText | None = toolsql.select(
        conn=conn,
        table=table,
        where_equals={'hash': hash},
        return_count='one',
        raise_if_table_dne=False,
    )

    if tx is None:
        return None
    else:
        return evm.convert_db_transaction_fields_to_int(tx)


async def async_select_transactions(
    hashes: typing.Sequence[str],
    *,
    conn: toolsql.SAConnection,
    context: spec.Context,
) -> typing.Sequence[spec.DBTransaction | None] | None:

    table = schema_utils.get_table_name('transactions', context=context)

    transactions: typing.Sequence[spec.DBTransaction] = toolsql.select(
        conn=conn,
        table=table,
        where_in={'hash': hashes},
        raise_if_table_dne=False,
    )

    if transactions is None:
        return None

    result = {tx['hash']: tx for tx in transactions}

    return [result.get(tx_hash) for tx_hash in hashes]


async def async_delete_transaction(
    hash: str,
    *,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:

    table = schema_utils.get_table_name('transactions', context=context)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'hash': hash},
    )


async def async_delete_transactions(
    hashes: typing.Sequence[str],
    *,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:

    if len(hashes) == 0:
        return

    table = schema_utils.get_table_name('transactions', context=context)

    toolsql.delete(
        conn=conn,
        table=table,
        where_in={'hash': hashes},
    )

