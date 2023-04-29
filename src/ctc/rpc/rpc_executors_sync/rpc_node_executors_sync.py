from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


def sync_web3_client_version(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_web3_client_version()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_web3_client_version(response=response)


def sync_web3_sha3(
    data: spec.BinaryData,
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_web3_sha3(data)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_web3_sha3(response=response)


def sync_net_version(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_net_version()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_net_version(response=response)


def sync_net_peer_count(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_net_peer_count()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_net_peer_count(response=response)


def sync_net_listening(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_net_listening()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_net_listening(response=response)


def sync_eth_protocol_version(
    *,
    context: spec.Context = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_protocol_version()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_protocol_version(
        response=response,
        decode_response=decode_response,
    )


def sync_eth_syncing(
    *,
    context: spec.Context = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_syncing()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_syncing(
        response=response,
        snake_case_response=snake_case_response,
    )


def sync_eth_chain_id(
    *,
    context: spec.Context = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_chain_id()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_chain_id(
        response=response,
        decode_response=decode_response,
    )

