from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from .. import rpc_format


#
# # helper decoding functions
#


def _decode_single_trace(trace: typing.Any) -> None:
    trace['action'] = rpc_format.decode_response(
        trace['action'],
        ['gas', 'value'],
    )
    if trace['result'] is not None:
        trace['result'] = rpc_format.decode_response(
            trace['result'],
            ['gasUsed'],
        )


def _decode_trace_list(traces: typing.Any) -> None:
    for trace in traces:
        _decode_single_trace(trace)


def _decode_trace_collection(traces: typing.Any) -> None:
    if traces['trace'] is not None:
        _decode_trace_list(traces['trace'])
    if traces.get('stateDiff') is not None:
        _decode_state_diff(traces['stateDiff'])


def _decode_state_diff(state_diff: spec.StateDiffTrace) -> None:

    for diff in state_diff.values():
        for key in ['balance', 'nonce']:
            subdiff = diff[key]  # type: ignore
            if isinstance(subdiff, dict):
                if '+' in subdiff:
                    subdiff['+'] = evm.binary_convert(subdiff['+'], 'integer')
                elif '*' in subdiff:
                    subdiff['*']['to'] = evm.binary_convert(
                        subdiff['*']['to'], 'integer'
                    )
                    subdiff['*']['from'] = evm.binary_convert(
                        subdiff['*']['from'], 'integer'
                    )
                elif '-' in subdiff:
                    subdiff['-'] = evm.binary_convert(subdiff['-'], 'integer')
                else:
                    raise Exception('unknown subdiff format')


def _snake_case_single_trace(trace: typing.Any) -> typing.Any:
    trace['action'] = rpc_format.keys_to_snake_case(trace['action'])
    if trace['result'] is not None:
        trace['result'] = rpc_format.keys_to_snake_case(trace['result'])
    return rpc_format.keys_to_snake_case(trace)


def _snake_case_trace_list(traces: typing.Any) -> typing.Any:
    traces = [rpc_format.keys_to_snake_case(trace) for trace in traces]
    return [_snake_case_single_trace(trace) for trace in traces]


def _snake_case_trace_collection(traces: typing.Any) -> None:

    if 'transactionHash' in traces:
        traces['transaction_hash'] = traces.pop('transactionHash')
    if 'vmTrace' in traces:
        traces['vm_trace'] = traces.pop('vmTrace')
    if 'stateDiff' in traces:
        traces['state_diff'] = traces.pop('stateDiff')

    if traces['trace'] is not None:
        traces['trace'] = _snake_case_trace_list(traces['trace'])


def _snake_case_debug_block_trace(trace: typing.Any) -> spec.DebugBlockTrace:
    return [_snake_case_debug_transaction_trace(tx_trace) for tx_trace in trace]


def _snake_case_debug_transaction_trace(
    trace: typing.Any,
) -> spec.DebugTransactionTrace:
    return {
        'struct_logs': _snake_case_debug_struct_log_traces(trace['structLogs']),
        'gas': trace['gas'],
        'failed': trace['failed'],
        'return_value': trace['returnValue'],
    }


def _snake_case_debug_struct_log_traces(
    traces: typing.Any,
) -> typing.Sequence[spec.DebugTraceStructLog]:
    for trace in traces:
        trace['gas_cost'] = trace.pop('gasCost')
    return traces  # type: ignore


#
# # transactions
#


def digest_trace_transaction(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        _decode_trace_list(response)

    if snake_case_response:
        response = _snake_case_trace_list(response)

    return response


def digest_trace_replay_transaction(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        _decode_trace_collection(response)

    if snake_case_response:
        _snake_case_trace_collection(response)

    return response


def digest_trace_raw_transaction(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    raise NotImplementedError()


#
# # calls
#


def digest_trace_call(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        _decode_trace_collection(response)

    if snake_case_response:
        _snake_case_trace_collection(response)

    return response


def digest_trace_call_many(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        for subresponse in response:
            _decode_trace_collection(subresponse)

    if snake_case_response:
        for subresponse in response:
            _snake_case_trace_collection(subresponse)

    return response


#
# # trace ranges
#


def digest_trace_get(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        _decode_single_trace(response)

    if snake_case_response:
        response = _snake_case_single_trace(response)

    return response


def digest_trace_filter(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        _decode_trace_list(response)

    if snake_case_response:
        response = _snake_case_trace_list(response)

    return response


def digest_trace_block(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        _decode_trace_list(response)

    if snake_case_response:
        response = _snake_case_trace_list(response)

    return response


def digest_trace_replay_block_transactions(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        for subtrace in response:
            _decode_trace_collection(subtrace)

    if snake_case_response:
        for subtrace in response:
            _snake_case_trace_collection(subtrace)

    return response


#
# # debug
#


def digest_debug_trace_call(
    response: spec.RpcSingularResponse,
    *,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if snake_case_response:
        response = _snake_case_debug_transaction_trace(response)

    return response


def digest_debug_trace_call_many(
    response: spec.RpcSingularResponse,
    *,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if snake_case_response:
        response = [
            _snake_case_debug_transaction_trace(subresponse)
            for subresponse in response
        ]

    return response


def digest_debug_trace_transaction(
    response: spec.RpcSingularResponse,
    *,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if snake_case_response:
        response = _snake_case_debug_transaction_trace(response)

    return response


def digest_debug_trace_block_by_number(
    response: spec.RpcSingularResponse,
    *,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if snake_case_response:
        response = _snake_case_debug_block_trace(response)

    return response


def digest_debug_trace_block_by_hash(
    response: spec.RpcSingularResponse,
    *,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if snake_case_response:
        response = _snake_case_debug_block_trace(response)

    return response

