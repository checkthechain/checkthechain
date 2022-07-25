from __future__ import annotations

import typing

from ctc import spec
from . import rpc_registry
from . import rpc_request


def construct(
    method: str,
    *,
    batch_parameter: typing.Optional[str] = None,
    batch_values: typing.Optional[list[typing.Any]] = None,
    **parameters: typing.Any,
) -> spec.RpcRequest:
    """create an rpc request according to a specific method"""
    constructor = rpc_registry.get_constructors()[method]
    if batch_parameter is not None and batch_values is not None:
        return [
            constructor(**{batch_parameter: value}, **parameters)
            for value in batch_values
        ]
    else:
        return constructor(**parameters)


def digest(
    response: spec.RpcRequest,
    request: spec.RpcResponse,
    *,
    digest_kwargs: typing.Optional[dict[typing.Any, typing.Any]] = None,
) -> spec.RpcResponse:
    """process an rpc response"""

    if isinstance(request, dict):
        digestor = rpc_registry.get_digestors()[request['method']]
        if digest_kwargs is None:
            digest_kwargs = {}

        if response is None:
            return response
        else:
            return digestor(response=response, **digest_kwargs)

    elif isinstance(request, list) and isinstance(response, list):
        output = []
        for subresponse, subrequest in zip(response, request):
            if subresponse is None:
                result = None
            else:
                result = digest(
                    subresponse,
                    subrequest,
                    digest_kwargs=digest_kwargs,
                )
            output.append(result)
        return output
    else:
        raise Exception()


async def async_execute(
    request: spec.RpcRequest,
    provider: spec.ProviderReference = None,
    *,
    digest_kwargs: typing.Optional[dict[typing.Any, typing.Any]] = None,
) -> spec.RpcResponse:
    response = await rpc_request.async_send(request=request, provider=provider)
    return digest(response, request=request, digest_kwargs=digest_kwargs)
