from __future__ import annotations

import typing
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


def _snake_case_single_trace(trace: typing.Any) -> None:
    trace['action'] = rpc_format.keys_to_snake_case(trace['action'])
    if trace['result'] is not None:
        trace['result'] = rpc_format.keys_to_snake_case(trace['result'])


def _snake_case_trace_list(traces: typing.Any) -> None:
    traces = [rpc_format.keys_to_snake_case(trace) for trace in traces]
    for trace in traces:
        _snake_case_single_trace(trace)


def _snake_case_trace_collection(traces: typing.Any) -> None:

    if 'transactionHash' in traces:
        traces['transaction_hash'] = traces.pop('transactionHash')
    if 'vmTrace' in traces:
        traces['vm_trace'] = traces.pop('vmTrace')
    if 'stateDiff' in traces:
        traces['state_diff'] = traces.pop('stateDiff')

    if traces['trace'] is not None:
        _snake_case_trace_list(traces['trace'])


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
        _snake_case_trace_list(response)

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
        _snake_case_single_trace(response)

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
        _snake_case_trace_list(response)

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

