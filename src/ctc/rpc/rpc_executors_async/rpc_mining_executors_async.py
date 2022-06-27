from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_get_work(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_work()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_work(response=response)


async def async_eth_submit_work(
    *,
    nonce: spec.BinaryData,
    pow_hash: spec.BinaryData,
    digest: spec.BinaryData,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_submit_work(
        nonce=nonce,
        pow_hash=pow_hash,
        digest=digest,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_submit_work(response=response)


async def async_eth_submit_hashrate(
    hashrate: spec.BinaryData,
    id: str,
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_submit_hashrate(
        hashrate=hashrate,
        id=id,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_submit_hashrate(response=response)


async def async_eth_coinbase(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_coinbase()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_coinbase(response=response)


async def async_eth_mining(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_mining()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_mining(response=response)


async def async_eth_hashrate(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_hashrate()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_hashrate(response=response)
