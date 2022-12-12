"""
"""

import typing

from ctc import spec
from .. import rpc_request


def construct_rpc_call(
    method: str,
    args: typing.Sequence[typing.Any] | None = None,
    kwargs: typing.Mapping[str, typing.Any] | None = None,
    arg_order: typing.Sequence[str] | None = None,
) -> spec.RpcRequest:
    return rpc_request.create


async def async_dispatch_rpc_call(
    request: spec.RpcRequest,
    provider: spec.ProviderReference = None,
) -> spec.RpcResponse:
    return rpc_request.async_send(request, provider=provider)


def digest_rpc_call(
    method: str,
    response: spec.RpcSingularResponse,
) -> typing.Any:
    return response


async def async_send_rpc_call(
    method: str,
    args: typing.Sequence[typing.Any] | None = None,
    kwargs: typing.Mapping[str, typing.Any] | None = None,
    arg_order: typing.Sequence[str] | None = None,
) -> spec.RpcResponse:

    request = construct_rpc_call(
        method=method,
        args=args,
        kwargs=kwargs,
        arg_order=arg_order,
    )

    response = await async_dispatch_rpc_call(
        method=method,
        request=request,
    )

    return digest_rpc_call(method=method, response=response)

