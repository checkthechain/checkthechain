import typing

from ctc import spec
from ctc.evm import block_utils
from ctc.evm import binary_utils
from ctc.evm import contract_abi_utils
from .. import rpc_request


def construct_rpc_eth_call(
    to_address: spec.BinaryData,
    from_address: spec.BinaryData = None,
    gas: spec.BinaryData = None,
    gas_price: spec.BinaryData = None,
    value_sent: spec.BinaryData = None,
    block_number: spec.BlockSpec = None,
    block_numbers: list[spec.BlockSpec] = None,
    call_data: spec.BinaryData = None,
    function_parameters: typing.Optional[typing.Union[list, dict]] = None,
    **function_abi_query
) -> spec.RpcResponse:
    if block_number is None and block_numbers is None:
        block_number = 'latest'
    if block_number is not None:
        block_number = block_utils.normalize_block(block=block_number)
        block_number = binary_utils.convert_binary_format(
            block_number, 'prefix_hex'
        )
    elif block_numbers is not None:
        encoded_block_numbers = []
        for block in block_numbers:
            block = block_utils.normalize_block(block=block)
            block = binary_utils.convert_binary_format(block, 'prefix_hex')
            encoded_block_numbers.append(block)
        block_numbers = encoded_block_numbers

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

    if block_number is not None:
        return rpc_request.create('eth_call', [call_object, block_number])
    elif block_numbers is not None:
        return [
            rpc_request.create('eth_call', [call_object, block_number])
            for block_number in block_numbers
        ]
    else:
        raise Exception('must specify block_number or block_numbers')


def construct_eth_estimate_gas(
    to_address: spec.BinaryData,
    from_address: spec.BinaryData = None,
    gas: spec.BinaryData = None,
    gas_price: spec.BinaryData = None,
    value_sent: spec.BinaryData = None,
    call_data: spec.BinaryData = None,
    function_parameters: typing.Optional[typing.Union[list, dict]] = None,
    **function_abi_query
) -> spec.RpcResponse:
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

    return rpc_request.create('eth_estimateGas', [call_object])


def construct_eth_get_balance(
    address,
    block_number='latest',
) -> spec.RpcResponse:

    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    return rpc_request.create('eth_getBalance', [address, block_number])


def construct_eth_get_storage_at(
    address: spec.BinaryData,
    position: spec.BinaryData,
    block_number='latest',
) -> spec.RpcResponse:
    position = binary_utils.convert_binary_format(position, 'prefix_hex')

    return rpc_request.create(
        'eth_getStorageAt', [address, position, block_number]
    )


def construct_eth_get_code(
    address: spec.BinaryData,
    block_number: spec.BlockSpec = 'latest',
) -> spec.RpcResponse:

    block_number = block_utils.normalize_block(block=block_number)
    block_number = binary_utils.convert_binary_format(
        block_number, 'prefix_hex'
    )

    return rpc_request.create('eth_getCode', [address, block_number])

