from ... import binary_utils
from .. import rpc_crud


def construct_eth_block_number():
    return rpc_crud.construct_rpc_call('eth_blockNumber', [])


def construct_eth_get_block_by_hash(
    block_hash, include_full_transactions=False
):
    encoded_block_hash = binary_utils.convert_binary_format(
        block_hash, 'prefix_hex'
    )
    parameters = [encoded_block_hash, include_full_transactions]
    return rpc_crud.construct_rpc_call('eth_getBlockByHash', parameters)


def construct_eth_get_block_by_number(
    block_number,
    include_full_transactions=True,
):

    encoded_block_number = rpc_crud.encode_rpc_block(block_number)

    parameters = [encoded_block_number, include_full_transactions]
    return rpc_crud.construct_rpc_call(
        method='eth_getBlockByNumber',
        parameters=parameters,
    )


def construct_eth_get_uncle_count_by_block_hash(block_hash):
    encoded_block_hash = binary_utils.convert_binary_format(
        block_hash, 'prefix_hex'
    )
    return rpc_crud.construct_rpc_call(
        method='eth_getUncleCountByBlockHash',
        parameters=[encoded_block_hash],
    )


def construct_eth_get_uncle_count_by_block_number(block_number):
    encoded_block_number = rpc_crud.encode_rpc_block(block_number)
    return rpc_crud.construct_rpc_call(
        method='eth_getUncleCountByBlockNumber',
        parameters=[encoded_block_number],
    )


def construct_eth_get_uncle_by_block_hash_and_index(block_hash, uncle_index):

    encoded_block_hash = binary_utils.convert_binary_format(
        block_hash, 'prefix_hex'
    )
    encoded_uncle_index = binary_utils.convert_binary_format(
        uncle_index, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call(
        method='eth_getUncleByBlockHashAndIndex',
        parameters=[encoded_block_hash, encoded_uncle_index],
    )


def construct_eth_get_uncle_by_block_number_and_index(
    block_number, uncle_index
):

    encoded_block_number = rpc_crud.encode_rpc_block(block_number)
    encoded_uncle_index = binary_utils.convert_binary_format(
        uncle_index, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call(
        method='eth_getUncleByBlockNumberAndIndex',
        parameters=[encoded_block_number, encoded_uncle_index],
    )

