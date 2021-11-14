import toolparallel

from ... import block_utils
from ... import binary_utils
from ... import contract_abi_utils
from .. import rpc_backends


@toolparallel.parallelize_input(
    singular_arg='block_number',
    plural_arg='block_numbers',
)
def eth_call(
    to_address,
    from_address=None,
    gas=None,
    gas_price=None,
    value_sent=None,
    block_number=None,
    call_data=None,
    function_parameters=None,
    provider=None,
    decode_result=True,
    delist_single_outputs=True,
    package_named_results=False,
    **function_abi_query
):
    if block_number is None:
        block_number = 'latest'
    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    # encode call data
    if call_data is None:
        call_data = contract_abi_utils.encode_call_data(
            parameters=function_parameters,
            contract_address=to_address,
            **function_abi_query
        )

    # assemble request data
    call_object = {
        'to': to_address,
        'data': call_data,
        'from': from_address,
        'gas': gas,
        'gasPrice': gas_price,
        'value': value_sent,
    }
    call_object = {k: v for k, v in call_object.items() if v is not None}

    # perform request
    result = rpc_backends.rpc_call(
        method='eth_call',
        parameters=[call_object, block_number],
        provider=provider,
    )

    # decode result
    if decode_result:
        result = contract_abi_utils.decode_function_output(
            encoded_output=result,
            contract_address=to_address,
            delist_single_outputs=delist_single_outputs,
            package_named_results=package_named_results,
            **function_abi_query
        )

    return result


def eth_estimate_gas(
    to_address,
    from_address=None,
    gas=None,
    gas_price=None,
    value_sent=None,
    call_data=None,
    function_parameters=None,
    provider=None,
    decode_result=True,
    **function_abi_query
):
    # encode call data
    if call_data is None:
        call_data = contract_abi_utils.encode_call_data(
            parameters=function_parameters,
            contract_address=to_address,
            **function_abi_query
        )

    # assemble call data
    call_object = {
        'to': to_address,
        'data': call_data,
        'from': from_address,
        'gas': gas,
        'gasPrice': gas_price,
        'value': value_sent,
    }
    call_object = {k: v for k, v in call_object.items() if v is not None}

    # perform call
    result = rpc_backends.rpc_call(
        method='eth_estimateGas',
        parameters=[call_object],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_get_balance(
    address, block_number='latest', provider=None, decode_result=True
):
    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    result = rpc_backends.rpc_call(
        method='eth_getBalance',
        parameters=[address, block_number],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_get_storage_at(address, position, block_number='latest', provider=None):
    position = binary_utils.convert_binary_format(position, 'prefix_hex')

    return rpc_backends.rpc_call(
        method='eth_getStorageAt',
        parameters=[address, position, block_number],
        provider=provider,
    )


def eth_get_code(address, block_number='latest', provider=None):
    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )
    return rpc_backends.rpc_call(
        method='eth_getCode',
        parameters=[address, block_number],
        provider=provider,
    )

