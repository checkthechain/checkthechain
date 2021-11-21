import anyio
import aiohttp

from ctc import spec
from .. import rpc_provider


_http_sessions: dict[spec.ProviderKey, aiohttp.ClientSession] = {}


async def async_send_http(
    request: spec.RequestData, provider: spec.Provider
) -> spec.ResponseData:
    provider = rpc_provider.get_provider(provider)
    session = get_async_http_session(provider=provider)
    async with session.post(provider['url'], json=request) as response:
        return await response.json()


def get_async_http_session(
    provider: spec.Provider, create: bool = True
) -> aiohttp.ClientSession:
    key = rpc_provider.get_provider_key(provider)
    if key not in _http_sessions:
        if create:
            kwargs = provider['session_kwargs']
            _http_sessions[key] = aiohttp.ClientSession(**kwargs)
        else:
            raise Exception('no session, must create')
    return _http_sessions[key]


async def async_close_session(provider: spec.Provider) -> None:
    session = get_async_http_session(provider=provider)
    await anyio.sleep(0)
    await session.close()

