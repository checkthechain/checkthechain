from __future__ import annotations

from ctc import evm
from ctc import spec
from .. import rpc_request


def construct_eth_get_transaction_count(
    from_address: spec.BinaryData,
    block_number: spec.BlockNumberReference = 'latest',
) -> spec.RpcRequest:

    block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        'eth_getTransactionCount',
        [from_address, block_number],
    )


def construct_eth_get_transaction_by_hash(
    transaction_hash: spec.BinaryData,
) -> spec.RpcRequest:
    return rpc_request.create('eth_getTransactionByHash', [transaction_hash])


def construct_eth_get_transaction_by_block_hash_and_index(
    block_hash: spec.BinaryData,
    transaction_index: spec.BinaryData,
) -> spec.RpcRequest:
    transaction_index = evm.binary_convert(transaction_index, 'prefix_hex')

    return rpc_request.create(
        'eth_getTransactionByBlockHashAndIndex',
        [block_hash, transaction_index],
    )


def construct_eth_get_transaction_by_block_number_and_index(
    block_number: spec.BlockNumberReference,
    transaction_index: spec.BinaryData,
) -> spec.RpcRequest:
    block_number = evm.encode_block_number(block_number)
    transaction_index = evm.binary_convert(transaction_index, 'prefix_hex')

    return rpc_request.create(
        'eth_getTransactionByBlockNumberAndIndex',
        [block_number, transaction_index],
    )


def construct_eth_get_transaction_receipt(
    transaction_hash: spec.BinaryData,
) -> spec.RpcRequest:
    return rpc_request.create(
        'eth_getTransactionReceipt',
        [transaction_hash],
    )


def construct_eth_get_block_transaction_count_by_hash(
    block_hash: spec.BinaryData,
) -> spec.RpcRequest:
    return rpc_request.create(
        'eth_getBlockTransactionCountByHash',
        [block_hash],
    )


def construct_eth_get_block_transaction_count_by_number(
    block_number: spec.BlockNumberReference,
) -> spec.RpcRequest:

    block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        'eth_getBlockTransactionCountByNumber',
        [block_number],
    )
