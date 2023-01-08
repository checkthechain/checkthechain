from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from ... import connect_utils
from ... import management
from . import transactions_statements


async def _async_convert_rpc_transaction_to_db_transaction(
    transaction: str | spec.DBTransaction | spec.RPCTransaction,
    *,
    context: spec.Context = None,
) -> spec.DBTransaction:

    from ctc import rpc

    if isinstance(transaction, str):
        tx: spec.RPCTransaction = await rpc.async_eth_get_transaction_by_hash(
            transaction,
            context=context,
        )
        transaction = tx

    if set(transaction.keys()) == spec.transaction_keys_db:

        return transaction  # type: ignore

    else:

        converted = {}
        need_receipt = False
        for k in spec.transaction_keys_db:
            if k not in transaction:
                if k in ['gas_used', 'gas_price']:
                    need_receipt = True
                else:
                    raise Exception('transaction is missing key: ' + str(k))
            else:
                converted[k] = transaction[k]  # type: ignore

        if need_receipt:

            receipt = await rpc.async_eth_get_transaction_receipt(
                transaction_hash=transaction['hash'],
                context=context,
            )
            for tx_key, receipt_key in [
                ['gas_used', 'gas_used'],
                ['gas_price', 'effective_gas_price'],
            ]:
                converted[tx_key] = receipt[receipt_key]

        return typing.cast(spec.DBTransaction, converted)


async def _async_convert_rpc_transactions_to_db_transactions(
    transactions: typing.Sequence[
        str | spec.DBTransaction | spec.RPCTransaction
    ],
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction]:

    import asyncio

    coroutines = [
        _async_convert_rpc_transaction_to_db_transaction(
            transaction=transaction,
            context=context,
        )
        for transaction in transactions
    ]
    return await asyncio.gather(*coroutines)


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

    db_txs = await _async_convert_rpc_transactions_to_db_transactions(
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
    transactions: typing.Sequence[spec.RPCTransaction],
    *,
    context: spec.Context,
) -> None:
    await async_intake_blocks_transactions(
        blocks_transactions={block_number: transactions},
        context=context,
    )


async def async_intake_blocks_transactions(
    blocks_transactions: typing.Mapping[int, typing.Sequence[spec.RPCTransaction]],
    *,
    context: spec.Context,
) -> None:
    raise NotImplementedError()


# async def async_intake_block_transaction_query(
#     block: spec. | spec.RPCBlock,
#     *,
#     latest_block: int | None = None,
#     context: spec.Context = None,
# ) -> None:

#     await async_intake_block_transaction_queries(
#         blocks=[block],
#         latest_block=latest_block,
#         context=context,
#     )


# async def async_intake_block_transaction_queries(
#     blocks: typing.Sequence[spec.DBBlockFullTxs | spec.RPCBlock],
#     *,
#     latest_block: int | None = None,
#     context: spec.Context = None,
# ) -> None:

#     import sqlalchemy.exc  # type: ignore

#     if latest_block is None:
#         latest_block = await evm.async_get_latest_block_number(context=context)

#     required_confirmations = management.get_required_confirmations(context=context)
#     latest_allowed_block = latest_block - required_confirmations
#     confirmed_blocks = [
#         block for block in blocks if block['number'] > latest_allowed_block
#     ]

#     engine = connect_utils.create_engine(schema_name='events', context=context)
#     if engine is None:
#         return None

#     if len(confirmed_blocks) == 0:
#         return

#     block_numbers = [block['number'] for block in confirmed_blocks]
#     transactions = await _async_convert_rpc_transactions_to_db_transactions(
#         [tx for block in confirmed_blocks for tx in block['transactions']],
#         context=context,
#     )

#     try:
#         with engine.begin() as conn:

#             await transactions_statements.async_upsert_block_transaction_queries(
#                 block_numbers=block_numbers,
#                 conn=conn,
#                 context=context,
#             )
#             await transactions_statements.async_upsert_transactions(
#                 transactions=transactions,
#                 conn=conn,
#                 context=context,
#             )

#     except sqlalchemy.exc.OperationalError:
#         pass

