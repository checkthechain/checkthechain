from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_request
from .. import rpc_digestors


def sync_eth_get_compilers(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_compilers()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_get_compilers(response=response)


def sync_eth_compile_lll(
    code: str, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_compile_lll(code=code)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_compile_lll(response=response)


def sync_eth_compile_solidity(
    code: str, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_compile_solidity(code=code)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_compile_solidity(response=response)


def sync_eth_compile_serpent(
    code: str, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_compile_serpent(code=code)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_compile_serpent(response=response)

