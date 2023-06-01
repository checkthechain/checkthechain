from __future__ import annotations

import typing

from ctc import spec
from ctc import evm
from .. import rpc_request


def construct_trace_transaction(
    transaction_hash: str,
) -> spec.RpcSingularRequest:
    return rpc_request.create(
        'trace_transaction',
        [transaction_hash],
    )


def construct_trace_replay_transaction(
    transaction_hash: str,
    trace_type: typing.Sequence[spec.TraceOutputType],
) -> spec.RpcSingularRequest:
    return rpc_request.create(
        'trace_replayTransaction',
        [transaction_hash, trace_type],
    )


def construct_trace_raw_transaction(
    call_data: str,
    trace_type: typing.Sequence[spec.TraceOutputType],
) -> spec.RpcSingularRequest:
    raise NotImplementedError()


#
# # calls
#


def construct_trace_call(
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
    block_number: spec.BlockNumberReference | None = None,
    trace_type: typing.Sequence[spec.TraceOutputType],
) -> spec.RpcSingularRequest:
    from . import rpc_state_constructors

    call = rpc_state_constructors.construct_eth_call(
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
    call['method'] = 'trace_call'
    tx, block_number = call['params']
    call['params'] = [tx, trace_type, block_number]
    return call


def construct_trace_call_many(
    calls: typing.Sequence[typing.Mapping[str, typing.Any]],
    trace_type: typing.Sequence[spec.TraceOutputType] | None,
    *,
    block_number: spec.BlockNumberReference | None = None,
) -> spec.RpcSingularRequest:
    """not an efficient implementation"""

    subrequests = []
    for call in calls:
        if 'block_number' in call:
            raise Exception('specify block_number as a top-level parameter')

        if call.get('trace_type') is not None:
            subrequest = construct_trace_call(**call)
        elif trace_type is not None:
            subrequest = construct_trace_call(trace_type=trace_type, **call)
        else:
            raise Exception('must specify trace_type')

        # parse out call
        sub_call, sub_trace_type, _ = subrequest['params']
        subrequests.append([sub_call, sub_trace_type])

    return rpc_request.create(
        'trace_callMany',
        [subrequests, block_number],
    )


#
# # trace ranges
#


def construct_trace_get(
    transaction_hash: str,
    trace_indices: typing.Sequence[int],
) -> spec.RpcSingularRequest:
    return rpc_request.create(
        'trace_get',
        [transaction_hash, trace_indices],
    )


def construct_trace_filter(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    from_addresses: spec.Address | None = None,
    to_addresses: spec.Address | None = None,
    after: int | None = None,
    count: int | None = None,
) -> spec.RpcSingularRequest:
    payload = {
        'start_block': start_block,
        'end_block': end_block,
        'from_addresses': from_addresses,
        'to_addresses': to_addresses,
        'after': after,
        'count': count,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return rpc_request.create(
        'trace_filter',
        [payload],
    )


def construct_trace_block(
    block_number: spec.BlockNumberReference,
) -> spec.RpcSingularRequest:
    block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        'trace_block',
        [block_number],
    )


def construct_trace_replay_block_transactions(
    block_number: spec.BlockNumberReference,
    trace_type: typing.Sequence[spec.TraceOutputType] | None,
) -> spec.RpcSingularRequest:
    block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        'trace_replayBlockTransactions',
        [block_number, trace_type],
    )


#
# # debug traces
#


def construct_debug_trace_call(
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
    block_number: spec.BlockNumberReference | None = None,
    trace_type: spec.TraceOutputType | None,
) -> spec.RpcSingularRequest:
    from . import rpc_state_constructors

    call = rpc_state_constructors.construct_eth_call(
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
    call['method'] = 'debug_traceCall'
    tx, block_number = call['params']
    call['params'] = [tx, block_number, trace_type]
    return call


def construct_debug_trace_call_many(
    calls: typing.Sequence[typing.Mapping[str, typing.Any]],
    trace_type: spec.TraceOutputType | None,
    *,
    block_number: spec.BlockNumberReference | None = None,
) -> spec.RpcSingularRequest:
    """not an efficient implementation"""

    subrequests = []
    for call in calls:
        if 'block_number' in call:
            raise Exception('specify block_number as a top-level parameter')

        if call.get('trace_type') is not None:
            subrequest = construct_debug_trace_call(**call)
        subrequest = construct_debug_trace_call(
            trace_type=trace_type,
            block_number=block_number,
            **call,
        )

        # parse out call
        sub_call, block_number, sub_trace_type = subrequest['params']
        subrequests.append([sub_call, sub_trace_type])

    return rpc_request.create(
        'debug_traceCallMany',
        [subrequests, block_number],
    )


def construct_debug_trace_transaction(
    transaction_hash: str,
    trace_type: spec.TraceOutputType | None = None,
) -> spec.RpcSingularRequest:
    return rpc_request.create(
        'debug_traceTransaction',
        [transaction_hash, trace_type],
    )


def construct_debug_trace_block_by_number(
    block_number: spec.BlockNumberReference,
    trace_type: spec.TraceOutputType | None = None,
) -> spec.RpcSingularRequest:
    block_number = evm.encode_block_number(block_number)
    return rpc_request.create(
        'debug_traceBlockByNumber',
        [block_number, trace_type],
    )


def construct_debug_trace_block_by_hash(
    block_hash: str,
) -> spec.RpcSingularRequest:
    return rpc_request.create(
        'debug_traceBlockByHash',
        [block_hash],
    )

