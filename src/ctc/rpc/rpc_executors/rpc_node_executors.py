from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_web3_client_version(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_web3_client_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_web3_client_version(response=response)


async def async_web3_sha3(
    data: spec.BinaryData,
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_web3_sha3(data)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_web3_sha3(response=response)


async def async_net_version(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_net_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_net_version(response=response)


async def async_net_peer_count(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_net_peer_count()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_net_peer_count(response=response)


async def async_net_listening(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_net_listening()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_net_listening(response=response)


async def async_eth_protocol_version(
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_protocol_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_protocol_version(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_syncing(
    *,
    provider: spec.ProviderReference = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_syncing()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_syncing(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_eth_chain_id(
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_chain_id()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_chain_id(
        response=response,
        decode_response=decode_response,
    )
