from __future__ import annotations

import typing
import warnings

if typing.TYPE_CHECKING:
    import aiohttp

from ctc import spec
from .. import rpc_provider


_http_sessions: dict[spec.ProviderKey, aiohttp.ClientSession] = {}


async def async_send_http(
    request: spec.RpcRequest,
    provider: spec.ProviderReference,
    *,
    n_attempts: int = 8,
) -> spec.RpcResponse:
    provider = rpc_provider.get_provider(provider)
    session = get_async_http_session(provider=provider)

    headers = {'User-Agent': 'ctc'}
    for attempt in range(n_attempts):

        async with session.post(
            provider['url'], json=request, headers=headers
        ) as response:
            if response.status != 200:
                import random

                t_sleep = 2 ** attempt + random.random()
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
            return await response.json()

    else:
        message = (
            'http rpc request failed after '
            + str(n_attempts)
            + ' retries, status_code = '
            + str(response.status)
        )
        # logger = logging.getLogger()
        # logger.info(message)
        raise Exception(message)


def get_async_http_session(
    provider: spec.Provider, create: bool = True
) -> aiohttp.ClientSession:

    key = rpc_provider.get_provider_key(provider)
    if key not in _http_sessions:
        if create:
            import aiohttp

            kwargs = provider['session_kwargs']
            if kwargs is None:
                kwargs = {}
            _http_sessions[key] = aiohttp.ClientSession(**kwargs)
        else:
            raise Exception('no session, must create')
    return _http_sessions[key]


async def async_close_http_session(
    provider: spec.ProviderReference = None,
) -> None:
    if len(_http_sessions) == 0:
        return

    if provider is None and len(_http_sessions) == 1:
        session = list(_http_sessions.values())[0]
    else:
        provider = rpc_provider.get_provider(provider)
        session = get_async_http_session(provider=provider)

    import asyncio

    await asyncio.sleep(0)
    await session.close()
