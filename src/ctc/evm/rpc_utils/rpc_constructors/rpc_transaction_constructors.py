from ... import binary_utils
from .. import rpc_crud


def construct_eth_get_transaction_count(from_address, block_number='latest'):
    return rpc_crud.construct_rpc_call(
        'eth_getTransactionCount',
        [from_address, block_number],
    )


def construct_eth_get_transaction_by_hash(transaction_hash):
    return rpc_crud.construct_rpc_call(
        'eth_getTransactionByHash', [transaction_hash]
    )


def construct_eth_get_transaction_by_block_hash_and_index(
    block_hash,
    transaction_index,
):
    transaction_index = binary_utils.convert_binary_format(
        transaction_index, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call(
        'eth_getTransactionByBlockHashAndIndex',
        [block_hash, transaction_index],
    )


def construct_eth_get_transaction_by_block_number_and_index(
    block_number,
    transaction_index,
):
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )
    transaction_index = binary_utils.convert_binary_format(
        transaction_index, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call(
        'eth_getTransactionByBlockNumberAndIndex',
        [block_number, transaction_index],
    )


def construct_eth_get_transaction_receipt(transaction_hash):
    return rpc_crud.construct_rpc_call(
        'eth_getTransactionReceipt',
        [transaction_hash],
    )


def construct_eth_get_block_transaction_count_by_hash(block_hash):
    return rpc_crud.construct_rpc_call(
        'eth_getBlockTransactionCountByHash',
        [block_hash],
    )


def construct_eth_get_block_transaction_count_by_number(block_number):
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call(
        'eth_getBlockTransactionCountByNumber',
        [block_number],
    )

