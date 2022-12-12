from __future__ import annotations

import typing
from typing_extensions import Literal

from ctc import spec

from .. import rpc_request


def construct_trace_transaction(
    transaction_hash: str,
) -> spec.RpcRequest:
    return rpc_request.create('trace_transaction', [transaction_hash])


def construct_trace_replay_transaction(
    transaction_hash: str,
    trace_type: typing.Sequence[Literal['vmTrace', 'trace', 'stateDiff']],
) -> spec.RpcRequest:
    return rpc_request.create(
        'trace_replayTransaction', [transaction_hash, trace_type]
    )


def digest_trace_transaction(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_trace_replay_transaction(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


async def async_trace_transaction(
    transaction_hash: str, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = construct_trace_transaction(transaction_hash=transaction_hash)
    response = await rpc_request.async_send(request, provider=provider)
    return digest_trace_transaction(response=response)


async def async_trace_replay_transaction(
    transaction_hash: str,
    trace_type: typing.Sequence[Literal['vmTrace', 'trace', 'stateDiff']],
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = construct_trace_replay_transaction(
        transaction_hash=transaction_hash, trace_type=trace_type
    )
    response = await rpc_request.async_send(request, provider=provider)
    return digest_trace_replay_transaction(response=response)

