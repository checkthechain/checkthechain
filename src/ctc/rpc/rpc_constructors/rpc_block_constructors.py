from __future__ import annotations

from ctc import evm
from ctc import spec

from .. import rpc_request


def construct_eth_block_number() -> spec.RpcRequest:
    return rpc_request.create('eth_blockNumber', [])


def construct_eth_get_block_by_hash(
    block_hash: spec.BinaryData,
    *,
    include_full_transactions: bool = False,
) -> spec.RpcRequest:
    encoded_block_hash = evm.binary_convert(block_hash, 'prefix_hex')
    parameters = [encoded_block_hash, include_full_transactions]
    return rpc_request.create('eth_getBlockByHash', parameters)


def construct_eth_get_block_by_number(
    block_number: spec.BlockNumberReference,
    *,
    include_full_transactions: bool = False,
) -> spec.RpcRequest:

    encoded_block_number = evm.encode_block_number(block_number)

    parameters = [encoded_block_number, include_full_transactions]
    return rpc_request.create(
        method='eth_getBlockByNumber',
        parameters=parameters,
    )


def construct_eth_get_uncle_count_by_block_hash(
    block_hash: spec.BinaryData,
) -> spec.RpcRequest:
    encoded_block_hash = evm.binary_convert(block_hash, 'prefix_hex')
    return rpc_request.create(
        method='eth_getUncleCountByBlockHash',
        parameters=[encoded_block_hash],
    )


def construct_eth_get_uncle_count_by_block_number(
    block_number: spec.BlockNumberReference,
) -> spec.RpcRequest:
    encoded_block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        method='eth_getUncleCountByBlockNumber',
        parameters=[encoded_block_number],
    )


def construct_eth_get_uncle_by_block_hash_and_index(
    block_hash: spec.BinaryData, uncle_index: spec.BinaryData
) -> spec.RpcRequest:

    encoded_block_hash = evm.binary_convert(block_hash, 'prefix_hex')
    encoded_uncle_index = evm.binary_convert(
        uncle_index, 'prefix_hex', keep_leading_0=False
    )

    return rpc_request.create(
        method='eth_getUncleByBlockHashAndIndex',
        parameters=[encoded_block_hash, encoded_uncle_index],
    )


def construct_eth_get_uncle_by_block_number_and_index(
    block_number: spec.BlockNumberReference, uncle_index: spec.BinaryData
) -> spec.RpcRequest:

    encoded_block_number = evm.encode_block_number(block_number)
    encoded_uncle_index = evm.binary_convert(
        uncle_index, 'prefix_hex', keep_leading_0=False
    )

    return rpc_request.create(
        method='eth_getUncleByBlockNumberAndIndex',
        parameters=[encoded_block_number, encoded_uncle_index],
    )
