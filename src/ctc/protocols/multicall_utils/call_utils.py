from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from . import multicall_spec


def get_call_contract(call: multicall_spec.Call) -> spec.Address:
    if isinstance(call, dict):
        return call['contract']
    elif isinstance(call, (list, tuple)):
        result = call[0]
        if not isinstance(result, str):
            raise Exception('bad format for call')
        return result
    else:
        raise Exception('unknown call format')


async def async_encode_call(
    call: multicall_spec.Call,
    *,
    context: spec.Context = None,
) -> tuple[spec.Address, spec.BinaryData]:
    contract = get_call_contract(call)
    call_data = await async_encode_call_data(call=call, context=context)
    return (contract, call_data)


async def async_encode_call_data(
    call: multicall_spec.Call,
    *,
    context: spec.Context = None,
) -> spec.BinaryData:

    # parse components
    if isinstance(call, dict):
        if 'call_data' in call:
            return typing.cast(multicall_spec.EncodedCallDict, call)[
                'call_data'
            ]
        elif 'function' in call:
            call = typing.cast(multicall_spec.UnencodedCallDict, call)
            contract = call['contract']
            function = call['function']
            function_parameters = call.get('function_parameters')

    elif isinstance(call, (list, tuple)):
        if len(call) == 2:
            contract, function = call
            function_parameters = None
        elif len(call) == 3:
            contract, function, function_parameters = call
        else:
            raise Exception('unknown call format')

    else:
        raise Exception('unknown call format')

    # get abi
    if isinstance(function, dict):
        function_abi = function
    elif isinstance(function, str):
        function_abi = await evm.async_get_function_abi(
            contract_address=contract,
            function_name=function,
            context=context,
        )
    else:
        raise Exception('could not determine function_abi')

    # encode
    encoded_data = evm.encode_call_data(
        function_abi=function_abi,
        parameters=function_parameters,
    )
    return evm.to_binary(encoded_data)


async def async_decode_call_output(
    call: multicall_spec.Call,
    encoded_output: spec.BinaryData,
    *,
    context: spec.Context = None,
) -> typing.Any:
    function_abi = await async_get_call_function_abi(call, context=context)
    return evm.decode_function_output(
        encoded_output=encoded_output,
        function_abi=function_abi,
    )


async def async_get_call_function_abi(
    call: multicall_spec.Call,
    *,
    context: spec.Context = None,
) -> spec.FunctionABI:

    function: spec.FunctionABI | str | None = None
    call_data: spec.BinaryData | None = None
    if isinstance(call, dict):
        if 'function' in call:
            function = typing.cast(multicall_spec.UnencodedCallDict, call)[
                'function'
            ]
        elif 'call_data' in call:
            call_data = typing.cast(multicall_spec.EncodedCallDict, call)[
                'call_data'
            ]
        else:
            raise Exception('unknown call format')
    elif isinstance(call, (list, tuple)):
        if isinstance(call[1], dict):
            if typing.TYPE_CHECKING:
                return typing.cast(spec.FunctionABI, call[1])
            else:
                return call[1]
        elif isinstance(call[1], str) and not call[1].startswith('0x'):
            function = call[1]
        else:
            call_data = call[1]
    else:
        raise Exception('unknown call format')

    if function is not None:
        if isinstance(function, dict):
            return function
        elif isinstance(function, str):
            return await evm.async_get_function_abi(
                contract_address=get_call_contract(call),
                function_name=function,
                context=context,
            )
        else:
            raise Exception('unknown call format')

    elif call_data is not None:
        call_data = evm.to_hex(call_data)
        function_selector = call_data[:10]
        return await evm.async_get_function_abi(
            contract_address=get_call_contract(call),
            function_selector=function_selector,
            context=context,
        )

    else:
        raise Exception('unknown call format')
