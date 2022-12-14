from __future__ import annotations

import typing

from ctc import evm
from ctc import spec


async def async_get_transaction(
    transaction_hash: str,
    *,
    use_db: bool = True,
    read_from_db: bool | None = None,
    write_to_db: bool | None = None,
    provider: spec.ProviderReference | None = None,
    network: spec.NetworkReference | None = None,
) -> spec.DBTransaction:
    """get transaction"""

    import asyncio
    from ctc import db
    from ctc import rpc

    network, provider = evm.get_network_and_provider(network, provider)

    # get from database
    if read_from_db is None:
        read_from_db = use_db
    if write_to_db is None:
        write_to_db = use_db
    if read_from_db:
        db_tx = await db.async_query_transaction(
            transaction_hash=transaction_hash,
            network=network,
        )
        if db_tx is not None:
            return db_tx

    # get from node
    raw_tx, raw_receipt = await asyncio.gather(
        rpc.async_eth_get_transaction_by_hash(
            transaction_hash,
            provider=provider,
        ),
        rpc.async_eth_get_transaction_receipt(
            transaction_hash,
            provider=provider,
        ),
    )

    # remove fields
    tx: spec.DBTransaction = {
        #
        # tx fields
        'transaction_hash': raw_tx['hash'],
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
        'effective_gas_price': raw_receipt['effective_gas_price'],
    }

    if write_to_db:
        await db.async_intake_transaction(
            transaction=tx,
            network=network,
        )

    return tx


async def async_get_transactions(
    transaction_hashes: typing.Sequence[str],
) -> list[spec.DBTransaction]:
    """get transactions"""

    import asyncio

    coroutines = [
        async_get_transaction(transaction_hash)
        for transaction_hash in transaction_hashes
    ]
    return await asyncio.gather(*coroutines)


#
# # transaction logs
#


async def async_get_transaction_logs(
    transaction_hash: str,
) -> typing.Sequence[spec.RawLog]:
    """get raw logs emitted by a transaction"""

    from ctc import rpc

    receipt: spec.TransactionReceipt = (
        await rpc.async_eth_get_transaction_receipt(transaction_hash)
    )

    return receipt['logs']


async def async_get_transactions_logs(
    transaction_hashes: typing.Sequence[str],
) -> typing.Sequence[spec.RawLog]:
    """get raw logs emitted by transactions"""

    from ctc import rpc

    receipts = await rpc.async_batch_eth_get_transaction_receipt(
        transaction_hashes=transaction_hashes,
    )

    return [log for receipt in receipts for log in receipt['logs']]


#
# # transactions of an adress
#


async def async_get_transaction_count(address: spec.Address) -> int:
    """get transaction count of address"""

    from ctc import rpc

    result = await rpc.async_eth_get_transaction_count(address)
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result

