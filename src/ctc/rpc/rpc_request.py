from __future__ import annotations

import asyncio
import logging
import math
import random
import typing

from ctc import spec
from . import rpc_provider


def create(method: str, parameters: list[typing.Any]) -> spec.RpcRequest:
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': random.randint(1, int(1e18)),
    }


def send(
    request: spec.RpcRequest,
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> spec.RpcResponse:
    full_provider = rpc_provider.get_provider(provider)

    if isinstance(request, dict):
        response = send_raw(request=request, provider=full_provider)
        return response['result']

    elif isinstance(request, list):

        # chunk request
        request_chunks = chunk_request(request=request, provider=full_provider)

        # send request chunks
        response_chunks = [
            send_raw(request=request_chunk, provider=full_provider)
            for request_chunk in request_chunks
        ]

        # reorder chunks
        plural_response = reorder_response_chunks(response_chunks, request)

        return [subresponse['result'] for subresponse in plural_response]

    else:

        raise Exception('unknown request type: ' + str(type(request)))


@typing.overload
def send_raw(
    request: spec.RpcSingularRequest, provider
) -> spec.RpcSingularResponseRaw:
    ...


@typing.overload
def send_raw(
    request: spec.RpcPluralRequest, provider
) -> spec.RpcPluralResponseRaw:
    ...


def send_raw(request: spec.RpcRequest, provider) -> spec.RpcResponseRaw:

    if provider['protocol'] == 'http':
        from .rpc_backends import rpc_http

        return rpc_http.send_http(
            request=request,
            provider=provider,
        )

    elif provider['protocol'] == 'websocket':
        from .rpc_backends import rpc_websocket

        return rpc_websocket.send_websocket(
            request=request,
            provider=provider,
        )

    else:
        raise Exception('unknown provider protocol: ' + str(provider['protocol']))


async def async_send(
    request: spec.RpcRequest,
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> spec.RpcResponse:
    full_provider = rpc_provider.get_provider(provider)

    if isinstance(request, dict):
        response = await async_send_raw(request=request, provider=full_provider)
        if 'result' not in response and 'error' in response:
            raise Exception('RPC ERROR: ' + response['error']['message'])
        return response['result']

    elif isinstance(request, list):

        # chunk request
        request_chunks = chunk_request(request=request, provider=full_provider)

        logger = logging.getLogger()
        logger.info(
            'chunking batch of '
            + str(len(request))
            + ' calls into '
            + str(len(request_chunks))
            + ' chunks'
        )

        # send request chunks
        coroutines = []
        for request_chunk in request_chunks:
            coroutine = async_send_raw(
                request=request_chunk,
                provider=full_provider,
            )
            coroutines.append(coroutine)
        response_chunks = await asyncio.gather(*coroutines)

        # reorder chunks
        plural_response = reorder_response_chunks(response_chunks, request)

        return [subresponse['result'] for subresponse in plural_response]

    else:

        raise Exception('unknown request type: ' + str(type(request)))


@typing.overload
async def async_send_raw(
    request: spec.RpcSingularRequest, provider
) -> spec.RpcSingularResponseRaw:
    ...


@typing.overload
async def async_send_raw(
    request: spec.RpcPluralRequest, provider
) -> spec.RpcPluralResponseRaw:
    ...


async def async_send_raw(
    request: spec.RpcRequest,
    provider: spec.Provider,
) -> spec.RpcResponseRaw:

    _log_request(request=request, provider=provider)

    if provider['protocol'] == 'http':
        from .rpc_backends import rpc_http_async

        return await rpc_http_async.async_send_http(
            request=request,
            provider=provider,
        )

    elif provider['protocol'] == 'websocket':
        from .rpc_backends import rpc_websocket_async

        return await rpc_websocket_async.async_send_websocket(
            request=request,
            provider=provider,
        )

    else:
        raise Exception('unknown provider protocol: ' + str(provider['protocol']))


def _log_request(request: spec.RpcRequest, provider: spec.Provider) -> None:
    logger = logging.getLogger()
    if isinstance(request, dict):
        logger.info('singular request: ' + request['method'])
    elif isinstance(request, list):
        methods = [subrequest['method'] for subrequest in request]
        logger.info(
            'plural request: '
            + str(len(request))
            + ' calls, '
            + str(set(methods))
        )
    else:
        raise Exception('unknown request type: ' + str(type(request)))


def reorder_response_chunks(
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


def chunk_request(
    request: spec.RpcPluralRequest, provider: spec.Provider
) -> list[spec.RpcPluralRequest]:

    if provider['chunk_size'] is not None:
        return chunk_request_by_size(request, provider['chunk_size'])
    else:
        return [request]


def chunk_request_by_size(
    request: spec.RpcPluralRequest, chunk_size: int
) -> list[spec.RpcPluralRequest]:

    n_chunks = math.ceil(len(request) / chunk_size)
    return [
        request[slice(c * chunk_size, (c + 1) * chunk_size)]
        for c in range(n_chunks)
    ]


def chunk_request_by_method(request):
    raise NotImplementedError()


def chunk_request_by_block_range(request):
    raise NotImplementedError()

