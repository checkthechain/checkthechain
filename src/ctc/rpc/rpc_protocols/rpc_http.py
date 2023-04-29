from __future__ import annotations

import typing
import warnings

if typing.TYPE_CHECKING:
    import aiohttp

from ctc import config
from ctc import spec
from .. import rpc_provider


_http_sessions: dict[spec.ProviderId, aiohttp.ClientSession] = {}


def sync_send_http(
    request: spec.RpcRequest,
    provider: spec.Provider,
    *,
    n_attempts: int = 8,
) -> str:
    import requests
    import json

    headers = {'Content-Type': 'application/json', 'User-Agent': 'ctc'}
    data = json.dumps(request)
    for attempt in range(n_attempts):
        try:
            response = requests.post(
                provider['url'],
                data=data,
                headers=headers,
            )
            return response.text
        except Exception:
            import time

            time.sleep(0.250)
    else:
        if response is None:
            status = 'None'
        else:
            status = str(response.status_code)
        message = (
            'http rpc request failed after '
            + str(n_attempts)
            + ' retries, status_code = '
            + str(status)
        )
        raise Exception(message)


async def async_send_http(
    request: spec.RpcRequest,
    provider: spec.Provider,
    *,
    n_attempts: int = 8,
) -> str:
    session = get_async_http_session(provider=provider)

    headers = {'User-Agent': 'ctc'}
    response = None
    for attempt in range(n_attempts):
        try:
            async with session.post(
                provider['url'], json=request, headers=headers
            ) as response:
                if response.status != 200:
                    import random

                    t_sleep = 2**attempt + random.random()
                    warnings.warn(
                        'request failed with code '
                        + str(response.status)
                        + ' retrying in '
                        + str(t_sleep)
                        + 's'
                    )
                    import asyncio

                    await asyncio.sleep(t_sleep)
                    continue
                as_text = await response.text()
                return as_text
        except Exception:
            # connection failure
            import asyncio

            await asyncio.sleep(0.250)

    else:
        if response is None:
            status = 'None'
        else:
            status = str(response.status)
        message = (
            'http rpc request failed after '
            + str(n_attempts)
            + ' retries, status_code = '
            + str(status)
        )
        raise Exception(message)


def get_async_http_session(
    provider: spec.Provider, create: bool = True
) -> aiohttp.ClientSession:
    provider_id = rpc_provider._get_provider_id(provider)
    if provider_id not in _http_sessions:
        if create:
            import aiohttp

            kwargs = provider['session_kwargs']
            if kwargs is None:
                kwargs = {}
            kwargs = dict(kwargs)
            kwargs.setdefault('timeout', aiohttp.ClientTimeout(300))
            _http_sessions[provider_id] = aiohttp.ClientSession(
                trust_env=True, **kwargs
            )
        else:
            raise Exception('no session, must create')
    return _http_sessions[provider_id]


async def async_close_http_session(
    context: spec.Context = None,
) -> None:
    import asyncio

    if len(_http_sessions) == 0:
        return

    if context is None:
        for key, session in list(_http_sessions.items()):
            await asyncio.sleep(0)
            await session.close()
            del _http_sessions[key]

    else:
        provider = config.get_context_provider(context)
        if provider is None:
            raise Exception('no provider available')
        session = get_async_http_session(provider=provider)
        session_keys = [
            key
            for key, value in _http_sessions.items()
            if id(session) == id(value)
        ]
        if len(session_keys) != 1:
            raise Exception('unknown session')
        else:
            session_key = session_keys[0]
        await asyncio.sleep(0)
        await session.close()
        del _http_sessions[session_key]

