from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


def sync_eth_get_work(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_work()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_get_work(response=response)


def sync_eth_submit_work(
    *,
    nonce: spec.BinaryData,
    pow_hash: spec.BinaryData,
    digest: spec.BinaryData,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_submit_work(
        nonce=nonce,
        pow_hash=pow_hash,
        digest=digest,
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_submit_work(response=response)


def sync_eth_submit_hashrate(
    hashrate: spec.BinaryData,
    id: str,
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_submit_hashrate(
        hashrate=hashrate,
        id=id,
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_submit_hashrate(response=response)


def sync_eth_coinbase(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_coinbase()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_coinbase(response=response)


def sync_eth_mining(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_mining()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_mining(response=response)


def sync_eth_hashrate(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_hashrate()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_hashrate(response=response)

