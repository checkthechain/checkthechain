from __future__ import annotations

import time
import typing
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    import asyncio

from .. import fourbyte_spec


class FourbyteRatelimit(TypedDict):
    requests_per_second: int | float
    last_request_time: int | float
    lock: asyncio.Lock | None


_4byte_ratelimit: FourbyteRatelimit = {
    'lock': None,
    'last_request_time': 0,
    'requests_per_second': 4.0,
}


async def async_query_remote_function_signatures(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> typing.Sequence[fourbyte_spec.Entry]:

    import aiohttp

    # get url template
    if id is not None:
        url_template = fourbyte_spec.endpoints['function_id']
    elif hex_signature is not None:
        url_template = fourbyte_spec.endpoints['function_hex']
    elif text_signature is not None:
        url_template = fourbyte_spec.endpoints['function_text']
    else:
        raise Exception('must specify id, hex_signature, or text_signature')

    # get url
    inputs = {
        'id': id,
        'bytes_signature': bytes_signature,
        'hex_signature': hex_signature,
        'text_signature': text_signature,
    }
    url = url_template.format(**inputs)

    # acquire lock
    import asyncio

    lock = _4byte_ratelimit['lock']
    if lock is None:
        lock = asyncio.Lock()
        _4byte_ratelimit['lock'] = lock

    # perform request
    async with lock:
        # ratelimit
        now = time.time()
        time_since_last = now - _4byte_ratelimit['last_request_time']
        seconds_per_request = 1 / _4byte_ratelimit['requests_per_second']
        time_to_sleep = seconds_per_request - time_since_last
        if time_to_sleep > 0:
            if True:
                print(
                    '4byte ratelimit hit, sleeping for '
                    + str(time_to_sleep)
                    + ' seconds (build local 4byte db to avoid)'
                )
            await asyncio.sleep(time_to_sleep)

        # perform request
        async with aiohttp.ClientSession() as session:

            # acquire, and retry if initial bad response
            async with session.get(url) as response:
                if response.status == 502:
                    await asyncio.sleep(3)
                else:
                    result = await response.json()
            async with session.get(url) as response:
                result = await response.json()

            _4byte_ratelimit['last_request_time'] = time.time()

            # process result
            if id is not None:
                return [result]
            else:
                return result['results']  # type: ignore


async def async_query_remote_event_signatures(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
) -> typing.Sequence[fourbyte_spec.Entry]:

    import aiohttp

    # get url template
    if id is not None:
        url_template = fourbyte_spec.endpoints['event_id']
    elif hex_signature is not None:
        url_template = fourbyte_spec.endpoints['event_hex']
    elif text_signature is not None:
        url_template = fourbyte_spec.endpoints['event_text']
    else:
        raise Exception('must specify id, hex_signature, or text_signature')

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
                return result['results']  # type: ignore
