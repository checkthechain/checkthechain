from ctc import spec

import websockets

from .. import rpc_provider


async def async_send_websocket(
    request: spec.RequestData,
    provider: spec.Provider,
) -> spec.ResponseData:
    provider = rpc_provider.get_provider(provider)
    async with websockets.connect(provider['url']) as websocket:
        await websocket.send(request)
        return await websocket.recv()

