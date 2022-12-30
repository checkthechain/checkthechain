from __future__ import annotations

import typing

from ctc import config
from ctc import spec


async def async_get_transaction(
    transaction_hash: str,
    *,
    context: spec.Context = None,
) -> spec.DBTransaction:
    """get transaction"""

    import asyncio
    from ctc import db
    from ctc import rpc

    # get from database
    read_cache, write_cache = config.get_context_cache_read_write(
        context=context, schema_name='transactions'
    )
    if read_cache:
        db_tx = await db.async_query_transaction(
            hash=transaction_hash,
            context=context,
        )
        if db_tx is not None:
            return db_tx

    # get from node
    raw_tx, raw_receipt = await asyncio.gather(
        rpc.async_eth_get_transaction_by_hash(
            transaction_hash,
            context=context,
        ),
        rpc.async_eth_get_transaction_receipt(
            transaction_hash,
            context=context,
        ),
    )

    # remove fields
    tx: spec.DBTransaction = {
        #
        # tx fields
        'hash': raw_tx['hash'],
        'block_number': raw_tx['block_number'],
        'transaction_index': raw_tx['transaction_index'],
        'to': raw_tx['to'],
        'from': raw_tx['from'],
        'value': raw_tx['value'],
        'input': raw_tx['input'],
        'nonce': raw_tx['nonce'],
        'type': raw_tx['type'],
        'access_list': raw_tx['access_list'],
        #
        # receipt fields
        'gas_used': raw_receipt['gas_used'],
        'gas_price': raw_receipt['effective_gas_price'],
    }

    if write_cache:
        await db.async_intake_transaction(transaction=tx, context=context)

    return tx


async def async_get_transactions(
    transaction_hashes: typing.Sequence[str],
    context: spec.Context = None,
) -> list[spec.DBTransaction]:
    """get transactions"""

    import asyncio

    coroutines = [
        async_get_transaction(transaction_hash, context=context)
        for transaction_hash in transaction_hashes
    ]
    return await asyncio.gather(*coroutines)


#
# # transaction logs
#


async def async_get_transaction_logs(
    transaction_hash: str,
    context: spec.Context = None,
) -> typing.Sequence[spec.RawLog]:
    """get raw logs emitted by a transaction"""

    from ctc import rpc

    receipt: spec.RPCTransactionReceipt = (
        await rpc.async_eth_get_transaction_receipt(
            transaction_hash, context=context
        )
    )

    return receipt['logs']


async def async_get_transactions_logs(
    transaction_hashes: typing.Sequence[str],
    context: spec.Context = None,
) -> typing.Sequence[spec.RawLog]:
    """get raw logs emitted by transactions"""

    from ctc import rpc

    receipts = await rpc.async_batch_eth_get_transaction_receipt(
        transaction_hashes=transaction_hashes, context=context
    )

    return [log for receipt in receipts for log in receipt['logs']]


#
# # transactions of an adress
#


async def async_get_transaction_count(
    address: spec.Address, context: spec.Context = None
) -> int:
    """get transaction count of address"""

    from ctc import rpc

    result = await rpc.async_eth_get_transaction_count(address, context=context)
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result

