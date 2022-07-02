from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request
from .. import rpc_provider


async def async_eth_call(
    to_address: spec.Address,
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
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    delist_single_outputs: bool = True,
    package_named_outputs: bool = False,
    fill_empty: bool = False,
    empty_token: typing.Any = None,
    function_abi: spec.FunctionABI | None = None,
    function_name: typing.Optional[str] = None,
    contract_abi: typing.Optional[spec.ContractABI] = None,
    n_parameters: typing.Optional[int] = None,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
    function_selector: typing.Optional[spec.FunctionSelector] = None,
) -> spec.RpcSingularResponse:

    if function_abi is None:
        if call_data is None or decode_response:
            function_abi = await evm.async_get_function_abi(
                contract_address=to_address,
                contract_abi=contract_abi,
                function_name=function_name,
                n_parameters=n_parameters,
                parameter_types=parameter_types,
                function_selector=function_selector,
                network=rpc_provider.get_provider_network(provider),
            )

    # construct request
    request = rpc_constructors.construct_eth_call(
        to_address=to_address,
        from_address=from_address,
        gas=gas,
        gas_price=gas_price,
        value_sent=value_sent,
        block_number=block_number,
        call_data=call_data,
        function_parameters=function_parameters,
        function_abi=function_abi,
    )

    # make request
    response = await rpc_request.async_send(request, provider=provider)

    # digest response
    return rpc_digestors.digest_eth_call(
        response,
        function_abi=function_abi,
        decode_response=decode_response,
        delist_single_outputs=delist_single_outputs,
        package_named_outputs=package_named_outputs,
        fill_empty=fill_empty,
        empty_token=empty_token,
    )


async def async_eth_estimate_gas(
    to_address: spec.Address,
    *,
    from_address: spec.BinaryData | None = None,
    gas: spec.BinaryData | None = None,
    gas_price: spec.BinaryData | None = None,
    value_sent: spec.BinaryData | None = None,
    call_data: spec.BinaryData | None = None,
    function_parameters: typing.Sequence[typing.Any]
    | typing.Mapping[str, typing.Any]
    | None = None,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    function_abi: spec.FunctionABI | None = None,
    function_name: typing.Optional[str] = None,
    contract_abi: typing.Optional[spec.ContractABI] = None,
    n_parameters: typing.Optional[int] = None,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
    function_selector: typing.Optional[spec.FunctionSelector] = None,
) -> spec.RpcSingularResponse:

    if function_abi is None:
        function_abi = await evm.async_get_function_abi(
            contract_address=to_address,
            contract_abi=contract_abi,
            function_name=function_name,
            n_parameters=n_parameters,
            parameter_types=parameter_types,
            function_selector=function_selector,
            network=rpc_provider.get_provider_network(provider),
        )

    request = rpc_constructors.construct_eth_estimate_gas(
        to_address=to_address,
        from_address=from_address,
        gas=gas,
        gas_price=gas_price,
        value_sent=value_sent,
        call_data=call_data,
        function_parameters=function_parameters,
        function_abi=function_abi,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_estimate_gas(
        response,
        decode_response=decode_response,
    )


async def async_eth_get_balance(
    address: spec.Address,
    *,
    block_number: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    if block_number is None:
        block_number = 'latest'
    request = rpc_constructors.construct_eth_get_balance(
        address=address,
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_balance(
        response,
        decode_response=decode_response,
    )


async def async_eth_get_storage_at(
    address: spec.Address,
    position: spec.BinaryData,
    *,
    block_number: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    if block_number is None:
        block_number = 'latest'
    request = rpc_constructors.construct_eth_get_storage_at(
        address=address,
        position=position,
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_storage_at(response)


async def async_eth_get_code(
    address: spec.Address,
    *,
    block_number: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    if block_number is None:
        block_number = 'latest'
    request = rpc_constructors.construct_eth_get_code(
        address=address,
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_code(response)
