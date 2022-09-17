from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from .. import rpc_request


def construct_eth_call(
    to_address: spec.BinaryData,
    *,
    from_address: spec.BinaryData | None = None,
    gas: spec.BinaryData | None = None,
    gas_price: spec.BinaryData | None = None,
    value_sent: spec.BinaryData | None = None,
    block_number: spec.BlockNumberReference | None = None,
    call_data: spec.BinaryData | None = None,
    function_parameters: typing.Sequence[typing.Any]
    | typing.Mapping[str, typing.Any]
    | None = None,
    function_abi: spec.FunctionABI | None = None,
) -> spec.RpcRequest:

    if block_number is None:
        block_number = 'latest'
    else:
        block_number = evm.encode_block_number(block_number)

    # encode call data
    if call_data is None:
        call_data = evm.encode_call_data(
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
    *,
    from_address: spec.BinaryData | None = None,
    gas: spec.BinaryData | None = None,
    gas_price: spec.BinaryData | None = None,
    value_sent: spec.BinaryData | None = None,
    call_data: spec.BinaryData | None = None,
    function_parameters: typing.Sequence[typing.Any]
    | typing.Mapping[str, typing.Any]
    | None = None,
    function_abi: spec.FunctionABI | None = None,
) -> spec.RpcRequest:

    # encode call data
    if call_data is None:
        call_data = evm.encode_call_data(
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
    address: spec.Address,
    *,
    block_number: spec.BlockNumberReference | None = None,
) -> spec.RpcRequest:

    if block_number is None:
        block_number = 'latest'

    encoded_block_number = evm.encode_block_number(block_number)
    return rpc_request.create('eth_getBalance', [address, encoded_block_number])


def construct_eth_get_storage_at(
    address: spec.BinaryData,
    position: spec.BinaryData,
    *,
    block_number: spec.BlockNumberReference = 'latest',
) -> spec.RpcRequest:

    position = evm.binary_convert(
        position, 'prefix_hex', keep_leading_0=False
    )
    encoded_block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        'eth_getStorageAt', [address, position, encoded_block_number]
    )


def construct_eth_get_code(
    address: spec.BinaryData,
    *,
    block_number: spec.BlockNumberReference = 'latest',
) -> spec.RpcRequest:

    block_number = evm.encode_block_number(block_number)
    return rpc_request.create('eth_getCode', [address, block_number])
