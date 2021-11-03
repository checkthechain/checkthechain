from ... import binary_utils
from .. import rpc_backends
from .. import rpc_coding
from .. import rpc_spec


def eth_get_transaction_count(
    from_address,
    block_number='latest',
    provider=None,
    decode_result=True,
):
    result = rpc_backends.rpc_call(
        method='eth_getTransactionCount',
        parameters=[from_address, block_number],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_get_transaction_by_hash(
    transaction_hash,
    provider=None,
    decode_result=True,
    snake_case_result=True,
):
    result = rpc_backends.rpc_call(
        method='eth_getTransactionByHash',
        parameters=[transaction_hash],
        provider=provider,
    )

    if decode_result:
        quantities = rpc_spec.rpc_transaction_quantities
        result = rpc_coding.decode_rpc_map(result, quantities)

    if snake_case_result:
        result = rpc_coding.rpc_keys_to_snake_case(result)

    return result


def eth_get_transaction_by_block_hash_and_index(
    block_hash,
    transaction_index,
    provider=None,
    decode_result=True,
    snake_case_result=True,
):
    transaction_index = binary_utils.convert_binary_format(
        transaction_index, 'prefix_hex'
    )

    result = rpc_backends.rpc_call(
        method='eth_getTransactionByBlockHashAndIndex',
        parameters=[block_hash, transaction_index],
        provider=provider,
    )

    if decode_result:
        quantities = rpc_spec.rpc_transaction_quantities
        result = rpc_coding.decode_rpc_map(result, quantities)

    if snake_case_result:
        result = rpc_coding.rpc_keys_to_snake_case(result)

    return result


def eth_get_transaction_by_block_number_and_index(
    block_number,
    transaction_index,
    provider=None,
    decode_result=True,
    snake_case_result=True,
):
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )
    transaction_index = binary_utils.convert_binary_format(
        transaction_index, 'prefix_hex'
    )

    result = rpc_backends.rpc_call(
        method='eth_getTransactionByBlockNumberAndIndex',
        parameters=[block_number, transaction_index],
        provider=provider,
    )

    if decode_result:
        quantities = rpc_spec.rpc_transaction_quantities
        result = rpc_coding.decode_rpc_map(result, quantities)

    if snake_case_result:
        result = rpc_coding.rpc_keys_to_snake_case(result)

    return result


def eth_get_transaction_receipt(
    transaction_hash,
    provider=None,
    decode_result=True,
    snake_case_result=True,
):
    result = rpc_backends.rpc_call(
        method='eth_getTransactionReceipt',
        parameters=[transaction_hash],
        provider=provider,
    )

    if decode_result:
        quantities = rpc_spec.rpc_transaction_receipt_quantities
        result = rpc_coding.decode_rpc_map(result, quantities)

    if snake_case_result:
        result = rpc_coding.rpc_keys_to_snake_case(result)

    return result


def eth_get_block_transaction_count_by_hash(
    block_hash, provider=None, decode_result=True,
):
    result = rpc_backends.rpc_call(
        method='eth_getBlockTransactionCountByHash',
        parameters=[block_hash],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_get_block_transaction_count_by_number(
    block_number, provider=None, decode_result=True
):
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    result = rpc_backends.rpc_call(
        method='eth_getBlockTransactionCountByNumber',
        parameters=[block_number],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result

