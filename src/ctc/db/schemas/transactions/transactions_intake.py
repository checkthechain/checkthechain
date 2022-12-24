from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from ... import connect_utils
from ... import management
from . import transactions_statements


async def _async_convert_rpc_transaction_to_db_transaction(
    transaction: str | spec.DBTransaction | spec.RPCTransaction,
    provider: spec.ProviderReference,
) -> spec.DBTransaction:

    from ctc import rpc

    if isinstance(transaction, str):
        tx: spec.RPCTransaction = await rpc.async_eth_get_transaction_by_hash(
            transaction
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
                provider=provider,
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
    provider: spec.ProviderReference,
) -> typing.Sequence[spec.DBTransaction]:

    import asyncio

    coroutines = [
        _async_convert_rpc_transaction_to_db_transaction(
            transaction=transaction,
            provider=provider,
        )
        for transaction in transactions
    ]
    return await asyncio.gather(*coroutines)


async def async_intake_transaction(
    transaction: spec.DBTransaction | spec.RPCTransaction,
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    latest_block: int | None = None,
) -> None:

    await async_intake_transactions(
        transactions=[transaction],
        network=network,
        provider=provider,
        latest_block=latest_block,
    )


async def async_intake_transactions(
    transactions: typing.Sequence[spec.DBTransaction | spec.RPCTransaction],
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    latest_block: int | None = None,
) -> None:

    network, provider = evm.get_network_and_provider(network, provider)

    if latest_block is None:
        latest_block = await evm.async_get_latest_block_number(
            provider=provider
        )
    required_confirmations = management.get_required_confirmations(network)
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
        provider=provider,
    )

    engine = connect_utils.create_engine(
        schema_name='transactions',
        network=network,
    )

    if engine is None:
        return

    with engine.connect() as conn:
        await transactions_statements.async_upsert_transactions(
            transactions=db_txs,
            network=network,
            conn=conn,
        )


async def async_intake_block_transaction_query(
    block: spec.Block | spec.RPCBlock,
    *,
    network: spec.NetworkReference,
    provider: spec.ProviderReference,
    latest_block: int | None = None,
) -> None:

    await async_intake_block_transaction_queries(
        blocks=[block],
        network=network,
        provider=provider,
        latest_block=latest_block,
    )


async def async_intake_block_transaction_queries(
    blocks: typing.Sequence[spec.Block | spec.RPCBlock],
    *,
    network: spec.NetworkReference,
    provider: spec.ProviderReference,
    latest_block: int | None = None,
) -> None:

    import sqlalchemy.exc  # type: ignore

    network, provider = evm.get_network_and_provider(network, provider)

    if latest_block is None:
        latest_block = await evm.async_get_latest_block_number(
            provider=provider
        )

    required_confirmations = management.get_required_confirmations(network)
    latest_allowed_block = latest_block - required_confirmations
    confirmed_blocks = [
        block for block in blocks if block['number'] > latest_allowed_block
    ]

    engine = connect_utils.create_engine(schema_name='events', network=network)
    if engine is None:
        return None

    if len(confirmed_blocks) == 0:
        return

    block_numbers = [block['number'] for block in confirmed_blocks]
    transactions = await _async_convert_rpc_transactions_to_db_transactions(
        [tx for block in confirmed_blocks for tx in block['transactions']],
        provider=provider,
    )

    try:
        with engine.begin() as conn:

            await transactions_statements.async_upsert_block_transaction_queries(
                block_numbers=block_numbers,
                conn=conn,
                network=network,
            )
            await transactions_statements.async_upsert_transactions(
                transactions=transactions,
                conn=conn,
                network=network,
            )

    except sqlalchemy.exc.OperationalError:
        pass

