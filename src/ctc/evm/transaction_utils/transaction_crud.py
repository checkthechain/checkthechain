from __future__ import annotations

import typing

from ctc import spec
from .. import block_utils
from . import transaction_convert


async def async_get_transaction(
    transaction_hash: str,
    *,
    context: spec.Context = None,
) -> spec.DBTransaction:
    """get transaction"""

    import asyncio
    from ctc import config
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

    db_transaction = (
        transaction_convert.convert_rpc_transaction_to_db_transaction(
            transaction=raw_tx, receipt=raw_receipt
        )
    )

    # remove fields
    if write_cache:
        await db.async_intake_transaction(
            transaction=db_transaction,
            context=context,
            already_converted=True,
        )

    return db_transaction


async def async_get_transactions(
    transaction_hashes: typing.Sequence[str],
    *,
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
# # block transactions
#


async def async_get_block_transactions(
    block: int,
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction]:
    """get all transactions in a block"""
    return await async_get_blocks_transactions(blocks=[block], context=context)


async def async_get_blocks_transactions(
    blocks: typing.Sequence[spec.BlockReference] | None = None,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction]:
    """get all transactions in collection of blocks"""

    import ctc.config
    import ctc.db

    if blocks is not None and (
        start_block is not None or end_block is not None
    ):
        raise Exception('cannot specify both blocks and start_block/end_block')
    if blocks is None and (start_block is None or end_block is None):
        raise Exception('must specify blocks or start_block+end_block')

    if blocks is not None:
        block_numbers = await block_utils.async_block_references_to_int(
            blocks=blocks, context=context
        )
    else:
        block_numbers = None

    # get from db
    read_cache, write_cache = ctc.config.get_context_cache_read_write(
        context=context,
        schema_name='transactions',
    )
    db_txs: typing.Sequence[spec.DBTransaction] = []
    if read_cache:

        result = await ctc.db.async_query_blocks_transactions(
            block_numbers=block_numbers,
            start_block=start_block,
            end_block=end_block,
            context=context,
        )
        if result is not None:
            db_txs, manifest = result
            missing_blocks = []

            if block_numbers is None:
                if start_block is None or end_block is None:
                    raise Exception('must specify more information about block range')
                start_block = await block_utils.async_block_number_to_int(
                    start_block, context=context
                )
                end_block = await block_utils.async_block_number_to_int(
                    end_block, context=context
                )
                block_numbers = list(range(start_block, end_block + 1))

            for block_number in block_numbers:
                if block_number not in manifest:
                    missing_blocks.append(block_number)
            if len(missing_blocks) == 0:
                return db_txs
            else:
                block_numbers = missing_blocks

    from ctc import rpc

    # get blocks from node
    rpc_blocks = await rpc.async_batch_eth_get_block_by_number(
        block_numbers=block_numbers,
        include_full_transactions=True,
        context=context,
    )

    # convert rpc txs to db txs
    rpc_transactions = [
        tx for rpc_block in rpc_blocks for tx in rpc_block['transactions']
    ]
    tx_hashes = [tx['hash'] for tx in rpc_transactions]
    rpc_receipts = await rpc.async_batch_eth_get_transaction_receipt(
        transaction_hashes=tx_hashes,
        context=context,
    )
    new_db_txs = [
        transaction_convert.convert_rpc_transaction_to_db_transaction(
            transaction=rpc_transaction, receipt=rpc_receipt
        )
        for rpc_transaction, rpc_receipt in zip(rpc_transactions, rpc_receipts)
    ]
    new_db_txs.extend(db_txs)

    if write_cache:
        await ctc.db.async_intake_blocks(
            rpc_blocks=rpc_blocks,
            context=context,
            blocks_db_transactions=new_db_txs,
        )

    return new_db_txs


#
# # transaction logs
#


async def async_get_transaction_logs(
    transaction_hash: str,
    *,
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
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.RawLog]:
    """get raw logs emitted by transactions"""

    from ctc import rpc

    receipts = await rpc.async_batch_eth_get_transaction_receipt(
        transaction_hashes=transaction_hashes, context=context
    )

    return [log for receipt in receipts for log in receipt['logs']]


#
# # transactions of an address
#


async def async_get_transaction_count(
    address: spec.Address, *, context: spec.Context = None
) -> int:
    """get transaction count of address"""

    from ctc import rpc

    result = await rpc.async_eth_get_transaction_count(address, context=context)
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result

