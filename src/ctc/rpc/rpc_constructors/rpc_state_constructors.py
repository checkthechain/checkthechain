import typing

from ctc import binary
from ctc import spec
from .. import rpc_request
from .. import rpc_format


def construct_eth_call(
    to_address: spec.BinaryData,
    from_address: spec.BinaryData = None,
    gas: spec.BinaryData = None,
    gas_price: spec.BinaryData = None,
    value_sent: spec.BinaryData = None,
    block_number: spec.BlockSpec = None,
    call_data: spec.BinaryData = None,
    function_parameters: typing.Optional[typing.Union[list, dict]] = None,
    function_abi: typing.Optional[spec.FunctionABI] = None,
) -> spec.RpcResponse:

    if block_number is None:
        block_number = 'latest'
    block_number = rpc_format.encode_block_number(block_number)

    # encode call data
    if call_data is None:
        call_data = binary.encode_call_data(
            parameters=function_parameters,
            function_abi=function_abi,
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

    return rpc_request.create('eth_call', [call_object, block_number])


def construct_eth_estimate_gas(
    to_address: spec.BinaryData,
    from_address: spec.BinaryData = None,
    gas: spec.BinaryData = None,
    gas_price: spec.BinaryData = None,
    value_sent: spec.BinaryData = None,
    call_data: spec.BinaryData = None,
    function_parameters: typing.Optional[typing.Union[list, dict]] = None,
    function_abi: typing.Optional[spec.FunctionABI] = None,
) -> spec.RpcResponse:

    # encode call data
    if call_data is None:
        call_data = binary.encode_call_data(
            parameters=function_parameters,
            function_abi=function_abi,
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
    block_number=None,
) -> spec.RpcResponse:

    if block_number is None:
        block_number = 'latest'

    block_number = rpc_format.encode_block_number(block_number)
    return rpc_request.create('eth_getBalance', [address, block_number])


def construct_eth_get_storage_at(
    address: spec.BinaryData,
    position: spec.BinaryData,
    block_number='latest',
) -> spec.RpcResponse:

    position = binary.convert(position, 'prefix_hex')
    block_number = rpc_format.encode_block_number(block_number)
    return rpc_request.create(
        'eth_getStorageAt', [address, position, block_number]
    )


def construct_eth_get_code(
    address: spec.BinaryData,
    block_number: spec.BlockSpec = 'latest',
) -> spec.RpcResponse:

    block_number = rpc_format.encode_block_number(block_number)
    return rpc_request.create('eth_getCode', [address, block_number])

