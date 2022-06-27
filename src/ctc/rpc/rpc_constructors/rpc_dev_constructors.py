from __future__ import annotations

from ctc import spec
from .. import rpc_request


def construct_eth_get_compilers() -> spec.RpcRequest:
    return rpc_request.create('eth_getCompilers', [])


def construct_eth_compile_lll(code: str) -> spec.RpcRequest:
    return rpc_request.create('eth_compileLLL', [code])


def construct_eth_compile_solidity(code: str) -> spec.RpcRequest:
    return rpc_request.create('eth_compileSolidity', [code])


def construct_eth_compile_serpent(code: str) -> spec.RpcRequest:
    return rpc_request.create('eth_compileSerpent', [code])
