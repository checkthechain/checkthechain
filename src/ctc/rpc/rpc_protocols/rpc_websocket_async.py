from __future__ import annotations

from ctc import spec


async def async_send_websocket(
    request: spec.RpcRequest,
    provider: spec.Provider,
) -> spec.RpcResponse:
    raise NotImplementedError()

