from __future__ import annotations

import typing

import aiohttp

from .. import fourbyte_spec


async def async_query_function_signature_remote(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:

    # get url template
    if id is not None:
        url_template = fourbyte_spec.endpoints['function_id']
    elif hex_signature is not None:
        url_template = fourbyte_spec.endpoints['function_hex']
    elif text_signature is not None:
        url_template = fourbyte_spec.endpoints['function_text']
    else:
        raise Exception()

    # get url
    inputs = {
        'id': id,
        'bytes_signature': bytes_signature,
        'hex_signature': hex_signature,
        'text_signature': text_signature,
    }
    url = url_template.format(**inputs)

    # perform request
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            if id is not None:
                return [result]
            else:
                return result['results']


async def async_query_event_signature_remote(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> list[fourbyte_spec.Entry]:

    # get url template
    if id is not None:
        url_template = fourbyte_spec.endpoints['event_id']
    elif hex_signature is not None:
        url_template = fourbyte_spec.endpoints['event_hex']
    elif text_signature is not None:
        url_template = fourbyte_spec.endpoints['event_text']
    else:
        raise Exception()

    # get url
    inputs = {
        'id': id,
        'bytes_signature': bytes_signature,
        'hex_signature': hex_signature,
        'text_signature': text_signature,
    }
    url = url_template.format(**inputs)

    # perform request
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            if id is not None:
                return [result]
            else:
                return result['results']

