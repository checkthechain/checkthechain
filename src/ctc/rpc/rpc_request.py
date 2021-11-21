import random
import typing

from ctc import spec
from . import rpc_provider


def create(method: str, parameters: list[typing.Any]) -> spec.RequestData:
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': random.randint(1, int(1e18)),
    }


def send(
    request: spec.RequestData,
    provider: typing.Optional[spec.ProviderSpec] = None,
    chunk: bool = True,
) -> spec.ResponseData:

    # get provider
    provider = rpc_provider.get_provider(provider)

    # send as chunks if specified
    if chunk and isinstance(request, list):
        request_chunks = chunk_request(request)
        chunk_responses = []
        for request_chunk in request_chunks:
            chunk_response = send(request_chunk, provider=provider, chunk=False)
            chunk_responses.append(chunk_response)
        return reorder_response_chunks(chunk_responses, request)

    # send request according to provider type
    if provider['type'] == 'http':
        from .rpc_backends import rpc_http

        response = rpc_http.send_http(
            request=request,
            provider=provider,
        )
    elif provider['type'] == 'websocket':
        from .rpc_backends import rpc_websocket

        response = rpc_websocket.send_websocket(
            request=request,
            provider=provider,
        )
    else:
        raise Exception('unknown provider type: ' + str(provider['type']))

    response = reorder_response(response, request)

    if isinstance(response, list):
        response = [subresponse['result'] for subresponse in response]
    elif isinstance(response, dict):
        response = response['result']
    else:
        raise Exception('unknown response type: ' + str(type(response)))

    return response


async def async_send(
    request: spec.RequestData,
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> spec.ResponseData:
    provider = rpc_provider.get_provider(provider)

    if provider['type'] == 'http':
        from .rpc_backends import rpc_http_async

        response = await rpc_http_async.async_send_http(
            request=request,
            provider=provider,
        )
    elif provider['type'] == 'websocket':
        from .rpc_backends import rpc_websocket_async

        response = await rpc_websocket_async.async_send_websocket(
            request=request,
            provider=provider,
        )

    else:
        raise Exception('unknown provider type: ' + str(provider['type']))

    response = reorder_response(response, request)

    if isinstance(response, list):
        response = [subresponse['result'] for subresponse in response]
    elif isinstance(response, dict):
        response = response['result']
    else:
        raise Exception('unknown response type: ' + str(type(response)))

    return response


def reorder_response(
    response: spec.ResponseData,
    request: spec.RequestData,
) -> spec.ResponseData:
    if isinstance(request, dict):
        return response
    elif isinstance(request, list) and isinstance(response, list):
        responses_by_id = {
            subresponse['id']: subresponse for subresponse in response
        }
        return [responses_by_id[subrequest['id']] for subrequest in request]
    else:
        raise Exception()


#
# # chunking
#


def chunk_request(request):
    return [request]


def chunk_request_by_method(request):
    raise NotImplementedError()


def chunk_request_by_size(request):
    raise NotImplementedError()


def chunk_request_by_block_range(request):
    raise NotImplementedError()


def reorder_response_chunks(response_chunks, request):
    raise NotImplementedError()

