from __future__ import annotations

from ctc import spec
from .. import rpc_request


def construct_eth_get_work() -> spec.RpcSingularRequest:
    return rpc_request.create('eth_getWork', [])


def construct_eth_submit_work(
    *,
    nonce: spec.BinaryData,
    pow_hash: spec.BinaryData,
    digest: spec.BinaryData,
) -> spec.RpcSingularRequest:
    parameters = [nonce, pow_hash, digest]
    return rpc_request.create('eth_submitWork', parameters)


def construct_eth_submit_hashrate(
    hashrate: spec.BinaryData, id: str
) -> spec.RpcSingularRequest:
    return rpc_request.create('eth_submitHashrate', [hashrate, id])


def construct_eth_coinbase() -> spec.RpcSingularRequest:
    return rpc_request.create('eth_coinbase', [])


def construct_eth_mining() -> spec.RpcSingularRequest:
    return rpc_request.create('eth_mining', [])


def construct_eth_hashrate() -> spec.RpcSingularRequest:
    return rpc_request.create('eth_hashrate', [])

