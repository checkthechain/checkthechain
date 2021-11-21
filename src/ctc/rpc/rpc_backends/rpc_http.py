from ctc import spec


def send_http(
    request: spec.RpcRequest, provider: spec.Provider
) -> spec.RpcResponse:
    raise NotImplementedError()

