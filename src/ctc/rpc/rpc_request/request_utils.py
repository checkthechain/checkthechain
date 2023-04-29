from __future__ import annotations

import typing

from ctc import spec
from .. import rpc_logging


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


def _postprocess_response(
    *,
    raw_response: str,
    request: spec.RpcRequest,
    provider: spec.Provider,
    raw_output: bool,
    convert_reverts_to: typing.Any = None,
    convert_reverts_to_none: bool = False,
    logging_rpc_calls: bool,
) -> typing.Any:

    if raw_output:
        return raw_response
    else:
        import orjson

        response = orjson.loads(raw_response)

    if 'result' not in response and 'error' in response:
        if provider['convert_reverts_to_none'] or convert_reverts_to_none:
            output = None
        elif convert_reverts_to is not None:
            output = convert_reverts_to
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

    return output


def _postprocess_plural_response(
    *,
    raw_response_chunks: typing.Sequence[str],
    request_chunks: list[spec.RpcPluralRequest],
    request: spec.RpcRequest,
    provider: spec.Provider,
    raw_output: bool,
    convert_reverts_to: typing.Any = None,
    convert_reverts_to_none: bool = False,
    logging_rpc_calls: bool,
) -> str | typing.Any:

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
    assert isinstance(request, list)
    plural_response = _reorder_response_chunks(response_chunks, request)

    if (
        provider['convert_reverts_to_none']
        or convert_reverts_to_none
        or convert_reverts_to is not None
    ):
        if convert_reverts_to is not None:
            revert_value = convert_reverts_to
        else:
            revert_value = None
        output = []
        for subresponse in plural_response:
            if 'result' in subresponse:
                output.append(subresponse['result'])
            elif 'error' in subresponse:
                output.append(revert_value)
            else:
                raise Exception('could not process response')
    else:
        output = [subresponse['result'] for subresponse in plural_response]

    return output


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
    import math

    n_chunks = math.ceil(len(request) / chunk_size)
    return [
        request[slice(c * chunk_size, (c + 1) * chunk_size)]
        for c in range(n_chunks)
    ]


def _chunk_request_by_method(request: spec.RpcRequest) -> None:
    raise NotImplementedError()


def _chunk_request_by_block_range(request: spec.RpcRequest) -> None:
    raise NotImplementedError()

