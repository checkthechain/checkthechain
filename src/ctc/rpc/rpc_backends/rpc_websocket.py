from ctc import spec


def send_websocket(
    request: spec.RpcRequest, provider: spec.Provider
) -> spec.RpcResponse:
    raise NotImplementedError()

