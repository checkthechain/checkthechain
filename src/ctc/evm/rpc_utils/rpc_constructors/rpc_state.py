from ... import block_utils
from ... import binary_utils
from ... import contract_abi_utils
from .. import rpc_crud


def construct_rpc_eth_call(
    to_address,
    from_address=None,
    gas=None,
    gas_price=None,
    value_sent=None,
    block_number=None,
    call_data=None,
    function_parameters=None,
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

    return rpc_crud.construct_rpc_call('eth_call', [call_object, block_number])


def construct_eth_estimate_gas(
    to_address,
    from_address=None,
    gas=None,
    gas_price=None,
    value_sent=None,
    call_data=None,
    function_parameters=None,
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

    return rpc_crud.construct_rpc_call('eth_estimateGas', [call_object])


def construct_eth_get_balance(address, block_number='latest'):

    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call(
        'eth_getBalance', [address, block_number]
    )


def eth_get_storage_at(address, position, block_number='latest'):
    position = binary_utils.convert_binary_format(position, 'prefix_hex')

    return rpc_crud.construct_rpc_call(
        'eth_getStorageAt', [address, position, block_number]
    )


def eth_get_code(address, block_number='latest', provider=None):

    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    return rpc_crud.construct_rpc_call('eth_getCode', [address, block_number])

