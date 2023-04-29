from __future__ import annotations

from ctc import spec


def sync_send_websocket(
    request: spec.RpcRequest,
    provider: spec.Provider,
) -> str:
    raise NotImplementedError()


async def async_send_websocket(
    request: spec.RpcRequest,
    provider: spec.Provider,
) -> str:
    raise NotImplementedError()

