from __future__ import annotations

from ctc import spec

from .. import rpc_request


def construct_trace_transaction(
    transaction_hash: str,
) -> spec.RpcRequest:
    return rpc_request.create('trace_transaction', [transaction_hash])


def digest_trace_transaction(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


async def async_trace_transaction(
    transaction_hash: str, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = construct_trace_transaction(transaction_hash=transaction_hash)
    response = await rpc_request.async_send(request, provider=provider)
    return digest_trace_transaction(response=response)
