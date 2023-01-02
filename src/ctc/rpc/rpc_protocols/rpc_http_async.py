from __future__ import annotations

import typing
import warnings

if typing.TYPE_CHECKING:
    import aiohttp

from ctc import config
from ctc import spec
from .. import rpc_provider


_http_sessions: dict[spec.ProviderId, aiohttp.ClientSession] = {}


async def async_send_http(
    request: spec.RpcRequest,
    provider: spec.Provider,
    *,
    n_attempts: int = 8,
) -> spec.RpcResponse:
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

    provider_id = rpc_provider._get_provider_id(provider)
    if provider_id not in _http_sessions:
        if create:
            import aiohttp

            kwargs = provider['session_kwargs']
            if kwargs is None:
                kwargs = {}
            _http_sessions[provider_id] = aiohttp.ClientSession(**kwargs)
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
        for session in _http_sessions.values():
            await asyncio.sleep(0)
            await session.close()

    else:
        provider = config.get_context_provider(context)
        if provider is None:
            raise Exception('no provider available')
        session = get_async_http_session(provider=provider)
        await asyncio.sleep(0)
        await session.close()

