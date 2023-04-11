from __future__ import annotations

import math
import typing

from ctc import spec
from . import rpc_logging


def create(
    method: str, parameters: list[typing.Any]
) -> spec.RpcSingularRequest:
    """create single RPC request given the RPC method and parameters"""

    import random

    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': random.randint(1, int(1e18)),
    }


@typing.overload
async def async_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: typing.Literal[True],
) -> str:
    ...


@typing.overload
async def async_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: typing.Literal[False] = False,
) -> spec.RpcResponse:
    ...


@typing.overload
async def async_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: bool,
) -> str | spec.RpcResponse:
    ...


async def async_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: bool = False,
) -> str | spec.RpcResponse:
    """send RPC request to RPC provider"""

    from ctc import config

    provider = config.get_context_provider(context)
    if provider is None:
        raise Exception('no provider available')

    try:
        logging_rpc_calls = config.get_log_rpc_calls()
    except Exception:
        logging_rpc_calls = False

    if isinstance(request, dict):

        if logging_rpc_calls:
            rpc_logging.log_rpc_request(request=request, provider=provider)

        raw_response = await async_send_raw(request=request, provider=provider)

        if raw_output:
            return raw_response
        else:
            import orjson

            response = orjson.loads(raw_response)

        if 'result' not in response and 'error' in response:
            if provider['convert_reverts_to_none']:
                output = None
            else:
                if typing.TYPE_CHECKING:
                    response = typing.cast(
                        spec.RpcSingularResponseFailure, response
                    )
                raise spec.RpcException(
                    'RPC ERROR: ' + response['error']['message']
                )
        else:
            if typing.TYPE_CHECKING:
                response = typing.cast(
                    spec.RpcSingularResponseSuccess, response
                )
            output = response['result']

        if logging_rpc_calls:
            rpc_logging.log_rpc_response(
                response=response,
                request=request,
                provider=provider,
            )

    elif isinstance(request, list):

        if len(request) == 0:
            return []

        if provider.get('disable_batch_requests'):
            import asyncio

            coroutines = [
                async_send(subrequest, context=context, raw_output=raw_output)
                for subrequest in request
            ]
            return await asyncio.gather(*coroutines)

        # chunk request
        request_chunks = _chunk_request(request=request, provider=provider)

        if logging_rpc_calls:
            for request_chunk in request_chunks:
                rpc_logging.log_rpc_request(
                    request=request_chunk, provider=provider
                )

        # send request chunks
        coroutines = []
        for request_chunk in request_chunks:
            coroutine = async_send_raw(
                request=request_chunk,
                provider=provider,
            )
            coroutines.append(coroutine)

        import asyncio

        raw_response_chunks = await asyncio.gather(*coroutines)
        if raw_output:
            return raw_response_chunks
        else:
            import orjson

            response_chunks = [
                orjson.loads(raw_response_chunk)
                for raw_response_chunk in raw_response_chunks
            ]

        if logging_rpc_calls:
            for request_chunk, response_chunk in zip(
                request_chunks, response_chunks
            ):
                rpc_logging.log_rpc_response(
                    response=response_chunk,
                    request=request_chunk,
                    provider=provider,
                )

        # reorder chunks
        plural_response = _reorder_response_chunks(response_chunks, request)

        if provider['convert_reverts_to_none']:
            output = []
            for subresponse in plural_response:
                if 'result' in subresponse:
                    output.append(subresponse['result'])
                elif 'error' in subresponse:
                    output.append(None)
                else:
                    raise Exception('could not process response')
        else:
            output = [subresponse['result'] for subresponse in plural_response]

    else:
        raise Exception('unknown request type: ' + str(type(request)))

    return output


# @typing.overload
# async def async_send_raw(
#     request: spec.RpcSingularRequest, provider: spec.Provider
# ) -> spec.RpcSingularResponseRaw:
#     ...


# @typing.overload
# async def async_send_raw(
#     request: spec.RpcPluralRequest, provider: spec.Provider
# ) -> spec.RpcPluralResponseRaw:
#     ...


# ) -> spec.RpcResponseRaw:
async def async_send_raw(
    request: spec.RpcRequest,
    provider: spec.Provider,
) -> str:
    """route RPC request to provider according to specified protocol"""

    if provider['protocol'] == 'http':
        from .rpc_protocols import rpc_http_async

        return await rpc_http_async.async_send_http(
            request=request,
            provider=provider,
        )

    elif provider['protocol'] == 'wss':
        from .rpc_protocols import rpc_websocket_async

        return await rpc_websocket_async.async_send_websocket(
            request=request,
            provider=provider,
        )

    else:
        raise Exception(
            'unknown provider protocol: ' + str(provider['protocol'])
        )


def _reorder_response_chunks(
    response_chunks: list[spec.RpcPluralResponseRaw],
    request: spec.RpcPluralRequest,
) -> spec.RpcPluralResponse:

    responses_by_id = {
        response['id']: response
        for response_chunk in response_chunks
        for response in response_chunk
    }
    return [responses_by_id[subrequest['id']] for subrequest in request]


#
# # chunking
#


def _chunk_request(
    request: spec.RpcPluralRequest, provider: spec.Provider
) -> list[spec.RpcPluralRequest]:

    if provider['chunk_size'] is not None:
        return _chunk_request_by_size(request, provider['chunk_size'])
    else:
        return [request]


def _chunk_request_by_size(
    request: spec.RpcPluralRequest, chunk_size: int
) -> list[spec.RpcPluralRequest]:

    n_chunks = math.ceil(len(request) / chunk_size)
    return [
        request[slice(c * chunk_size, (c + 1) * chunk_size)]
        for c in range(n_chunks)
    ]


def _chunk_request_by_method(request: spec.RpcRequest) -> None:
    raise NotImplementedError()


def _chunk_request_by_block_range(request: spec.RpcRequest) -> None:
    raise NotImplementedError()

