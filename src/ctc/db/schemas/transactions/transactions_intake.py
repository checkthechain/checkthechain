from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from ... import connect_utils
from ... import management
from . import transactions_statements


async def async_intake_transaction(
    transaction: spec.DBTransaction | spec.RPCTransaction,
    *,
    context: spec.Context = None,
    latest_block: int | None = None,
) -> None:

    await async_intake_transactions(
        transactions=[transaction],
        latest_block=latest_block,
        context=context,
    )


async def async_intake_transactions(
    transactions: typing.Sequence[spec.DBTransaction | spec.RPCTransaction],
    *,
    latest_block: int | None = None,
    context: spec.Context = None,
) -> None:

    if latest_block is None:
        latest_block = await evm.async_get_latest_block_number(context=context)
    required_confirmations = management.get_required_confirmations(
        context=context
    )
    latest_allowed_block = latest_block - required_confirmations
    confirmed_txs = [
        transaction
        for transaction in transactions
        if transaction['block_number'] <= latest_allowed_block
    ]

    if len(confirmed_txs) == 0:
        return

    db_txs = await evm.async_convert_rpc_transactions_to_db_transactions(
        confirmed_txs,
        context=context,
    )

    engine = connect_utils.create_engine(
        schema_name='transactions',
        context=context,
    )

    if engine is None:
        return

    with engine.connect() as conn:
        await transactions_statements.async_upsert_transactions(
            transactions=db_txs,
            conn=conn,
            context=context,
        )


async def async_intake_block_transactions(
    block_number: int,
    transactions: typing.Sequence[spec.DBTransaction],
    *,
    context: spec.Context,
) -> None:
    await async_intake_blocks_transactions(
        block_numbers=[block_number],
        transactions=transactions,
        context=context,
    )


async def async_intake_blocks_transactions(
    block_numbers: typing.Sequence[int],
    transactions: typing.Sequence[spec.DBTransaction],
    *,
    context: spec.Context,
) -> None:

    if len(block_numbers) == 0:
        if len(transactions) > 0:
            raise Exception('must specify block_numbers alongside transactions')
        return

    engine = connect_utils.create_engine(
        schema_name='transactions',
        context=context,
    )
    if engine is None:
        return

    with engine.connect() as conn:
        await transactions_statements.async_upsert_block_transaction_queries(
            block_numbers=block_numbers,
            conn=conn,
            context=context,
        )
        await transactions_statements.async_upsert_transactions(
            transactions=transactions,
            conn=conn,
            context=context,
        )

