from __future__ import annotations

import typing

from ctc import spec
from .. import rpc_logging
from . import request_utils


@typing.overload
def sync_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: typing.Literal[True],
    convert_reverts_to: typing.Any = None,
    convert_reverts_to_none: bool = False,
) -> str:
    ...


@typing.overload
def sync_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: typing.Literal[False] = False,
    convert_reverts_to: typing.Any = None,
    convert_reverts_to_none: bool = False,
) -> spec.RpcResponse:
    ...


@typing.overload
def sync_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: bool,
    convert_reverts_to: typing.Any = None,
    convert_reverts_to_none: bool = False,
) -> str | spec.RpcResponse:
    ...


def sync_send(
    request: spec.RpcRequest,
    *,
    context: spec.Context = None,
    raw_output: bool = False,
    convert_reverts_to: typing.Any = None,
    convert_reverts_to_none: bool = False,
) -> str | spec.RpcResponse:
    """send RPC request to RPC provider"""

    from ctc import config

    # get provider
    provider = config.get_context_provider(context)
    if provider is None:
        raise Exception('no provider available')

    try:
        logging_rpc_calls = config.get_log_rpc_calls()
    except Exception:
        logging_rpc_calls = False

    if isinstance(request, dict):
        # log request
        if logging_rpc_calls:
            rpc_logging.log_rpc_request(request=request, provider=provider)

        # send request
        raw_response = sync_send_raw(request=request, provider=provider)

        # process response
        output = request_utils._postprocess_response(
            raw_response=raw_response,
            request=request,
            provider=provider,
            raw_output=raw_output,
            convert_reverts_to_none=convert_reverts_to_none,
            convert_reverts_to=convert_reverts_to,
            logging_rpc_calls=logging_rpc_calls,
        )

    elif isinstance(request, list):
        # circuit break for empty batch request
        if len(request) == 0:
            return []

        # break into individual requests if batch disabled
        if provider.get('disable_batch_requests'):
            results = []
            for subrequest in request:
                result = sync_send(
                    subrequest,
                    context=context,
                    raw_output=raw_output,
                    convert_reverts_to=convert_reverts_to,
                    convert_reverts_to_none=convert_reverts_to_none,
                )
                results.append(result)
            return results

        # chunk request
        request_chunks = request_utils._chunk_request(
            request=request, provider=provider
        )

        # log requests
        if logging_rpc_calls:
            for request_chunk in request_chunks:
                rpc_logging.log_rpc_request(
                    request=request_chunk, provider=provider
                )

        # send request chunks
        raw_response_chunks = []
        for request_chunk in request_chunks:
            result = sync_send_raw(request=request_chunk, provider=provider)
            raw_response_chunks.append(result)

        # process responses
        output = request_utils._postprocess_plural_response(
            raw_response_chunks=raw_response_chunks,
            request_chunks=request_chunks,
            request=request,
            provider=provider,
            raw_output=raw_output,
            convert_reverts_to_none=convert_reverts_to_none,
            convert_reverts_to=convert_reverts_to,
            logging_rpc_calls=logging_rpc_calls,
        )

    else:
        raise Exception('unknown request type: ' + str(type(request)))

    return output


def sync_send_raw(
    request: spec.RpcRequest,
    provider: spec.Provider,
) -> str:
    """route RPC request to provider according to specified protocol"""

    if provider['protocol'] == 'http':
        from ..rpc_protocols import rpc_http

        return rpc_http.sync_send_http(
            request=request,
            provider=provider,
        )

    elif provider['protocol'] == 'wss':
        from ..rpc_protocols import rpc_websocket

        return rpc_websocket.sync_send_websocket(
            request=request,
            provider=provider,
        )

    else:
        raise Exception(
            'unknown provider protocol: ' + str(provider['protocol'])
        )

