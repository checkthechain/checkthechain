from __future__ import annotations

import typing

from ctc import spec


#
# # basic conversion
#

def convert_rpc_transaction_to_db_transaction(
    transaction: spec.RPCTransaction,
    receipt: spec.RPCTransactionReceipt,
) -> spec.DBTransaction:
    """convert transaction data from rpc call into db transaction format"""

    if set(transaction.keys()) == spec.db_transaction_keys:
        return transaction  # type: ignore

    to = transaction.get('to')
    if to is None:
        to = '0x0000000000000000000000000000000000000000'

    tx: spec.DBTransaction = {
        #
        # tx fields
        'hash': transaction['hash'],
        'block_number': transaction['block_number'],
        'transaction_index': transaction['transaction_index'],
        'to_address': to,
        'from_address': transaction['from'],
        'value': transaction['value'],
        'input': transaction['input'],
        'nonce': transaction['nonce'],
        'transaction_type': transaction['type'],
        'access_list': transaction.get('access_list'),
        #
        # receipt fields
        'gas_used': receipt['gas_used'],
        'gas_price': receipt['effective_gas_price'],
        'gas_limit': transaction['gas'],
        'gas_priority': transaction.get('max_priority_fee_per_gas'),
        'gas_price_max': transaction.get('max_fee_per_gas'),
        'status': bool(receipt['status']),
    }
    return tx


#
# # conversions that require fetching data
#

async def async_convert_rpc_transaction_to_db_transaction(
    transaction: spec.DBTransaction | spec.RPCTransaction,
    *,
    context: spec.Context = None,
) -> spec.DBTransaction:
    """convert transaction to standard form, fetching receipts as necessary"""

    from ctc import rpc

    if set(transaction.keys()) == spec.db_transaction_keys:
        return transaction  # type: ignore
    else:
        receipt = await rpc.async_eth_get_transaction_receipt(
            transaction_hash=transaction['hash'],
            context=context,
        )
        return convert_rpc_transaction_to_db_transaction(
            transaction=transaction,  # type: ignore
            receipt=receipt,
        )


async def async_convert_rpc_transactions_to_db_transactions(
    transactions: typing.Sequence[spec.DBTransaction | spec.RPCTransaction],
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction]:
    """convert transactions to standard form, fetching receipts as necessary"""

    import asyncio

    coroutines = [
        async_convert_rpc_transaction_to_db_transaction(
            transaction=transaction,
            context=context,
        )
        for transaction in transactions
    ]
    return await asyncio.gather(*coroutines)


#
# # text <--> int conversion
#

def convert_db_transaction_fields_to_text(
    transaction: spec.DBTransaction,
    *,
    inplace: bool = False,
) -> spec.DBTransactionText:
    """convert large integer transaction fields from int to text"""
    if not inplace:
        transaction = transaction.copy()
    field: typing.Literal['value']
    for field in ['value']:  # type: ignore
        transaction[field] = str(transaction[field])  # type: ignore
    return transaction  # type: ignore


def convert_db_transaction_fields_to_int(
    transaction: spec.DBTransactionText,
    *,
    inplace: bool = False,
) -> spec.DBTransaction:
    """convert large integer transaction fields from text to int"""
    if not inplace:
        transaction = transaction.copy()
    field: typing.Literal['value']
    for field in ['value']:  # type: ignore
        transaction[field] = int(transaction[field])  # type: ignore
    return transaction  # type: ignore

