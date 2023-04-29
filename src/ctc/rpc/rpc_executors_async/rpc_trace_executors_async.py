from __future__ import annotations

import typing

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_trace_transaction(
    transaction_hash: str,
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_transaction(
        transaction_hash=transaction_hash
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_trace_transaction(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_trace_replay_transaction(
    transaction_hash: str,
    trace_type: typing.Sequence[spec.TraceOutputType],
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_replay_transaction(
        transaction_hash=transaction_hash, trace_type=trace_type
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_trace_replay_transaction(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_trace_raw_transaction(
    call_data: str,
    trace_type: typing.Sequence[spec.TraceOutputType],
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    raise NotImplementedError()


#
# # calls
#


async def async_trace_call(
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
    trace_type: typing.Sequence[spec.TraceOutputType],
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    block_number: spec.BlockNumberReference | None = None,
) -> spec.RpcSingularResponse:

    request = rpc_constructors.construct_trace_call(
        to_address=to_address,
        from_address=from_address,
        gas=gas,
        gas_price=gas_price,
        value_sent=value_sent,
        block_number=block_number,
        call_data=call_data,
        function_parameters=function_parameters,
        function_abi=function_abi,
        trace_type=trace_type,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_trace_call(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_trace_call_many(
    calls: typing.Sequence[typing.Mapping[str, typing.Any]],
    trace_type: typing.Sequence[spec.TraceOutputType] | None,
    *,
    block_number: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_call_many(
        calls=calls,
        trace_type=trace_type,
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_trace_call_many(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


#
# # trace ranges
#


async def async_trace_get(
    transaction_hash: spec.TransactionHash,
    trace_indices: typing.Sequence[int],
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_get(
        transaction_hash=transaction_hash,
        trace_indices=trace_indices,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_trace_get(response=response)


async def async_trace_filter(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    from_addresses: spec.Address | None = None,
    to_addresses: spec.Address | None = None,
    after: int | None = None,
    count: int | None = None,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_filter(
        start_block=start_block,
        end_block=end_block,
        from_addresses=from_addresses,
        to_addresses=to_addresses,
        after=after,
        count=count,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_trace_filter(response=response)


async def async_trace_block(
    block_number: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    raw_output: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_block(
        block_number=block_number,
    )
    response = await rpc_request.async_send(
        request, context=context, raw_output=raw_output
    )
    if raw_output:
        return response
    else:
        return rpc_digestors.digest_trace_block(
            response=response,
            decode_response=decode_response,
            snake_case_response=snake_case_response,
        )


async def async_trace_replay_block_transactions(
    block_number: spec.BlockNumberReference,
    trace_type: typing.Sequence[spec.TraceOutputType] | None,
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    raw_output: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_trace_replay_block_transactions(
        block_number=block_number,
        trace_type=trace_type,
    )
    response = await rpc_request.async_send(
        request,
        context=context,
        raw_output=raw_output,
    )
    if raw_output:
        return response
    else:
        return rpc_digestors.digest_trace_replay_block_transactions(
            response=response,
            decode_response=decode_response,
            snake_case_response=snake_case_response,
        )


#
# # debug traces
#


async def async_debug_trace_call(
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
    trace_type: spec.TraceOutputType,
    context: spec.Context = None,
    snake_case_response: bool = True,
    block_number: spec.BlockNumberReference | None = None,
) -> spec.RpcSingularResponse:

    request = rpc_constructors.construct_debug_trace_call(
        to_address=to_address,
        from_address=from_address,
        gas=gas,
        gas_price=gas_price,
        value_sent=value_sent,
        block_number=block_number,
        call_data=call_data,
        function_parameters=function_parameters,
        function_abi=function_abi,
        trace_type=trace_type,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_debug_trace_call(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_debug_trace_call_many(
    calls: typing.Sequence[typing.Mapping[str, typing.Any]],
    trace_type: spec.TraceOutputType | None,
    *,
    block_number: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_debug_trace_call_many(
        calls=calls,
        trace_type=trace_type,
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_debug_trace_call_many(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_debug_trace_transaction(
    transaction_hash: str,
    *,
    context: spec.Context = None,
    trace_type: spec.TraceOutputType | None = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    request = rpc_constructors.construct_debug_trace_transaction(
        transaction_hash=transaction_hash,
        trace_type=trace_type,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_debug_trace_transaction(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_debug_trace_block_by_number(
    block_number: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
    trace_type: spec.TraceOutputType | None = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_debug_trace_block_by_number(
        block_number=block_number,
        trace_type=trace_type,
    )
    response = await rpc_request.async_send(
        request,
        context=context,
    )
    return rpc_digestors.digest_debug_trace_block_by_number(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_debug_trace_block_by_hash(
    block_hash: str,
    *,
    context: spec.Context = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_debug_trace_block_by_hash(
        block_hash=block_hash,
    )
    response = await rpc_request.async_send(request, context=context)
    return rpc_digestors.digest_debug_trace_block_by_hash(
        response=response,
        snake_case_response=snake_case_response,
    )

