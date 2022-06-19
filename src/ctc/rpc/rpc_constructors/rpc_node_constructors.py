from __future__ import annotations

from ctc import spec
from .. import rpc_request


def construct_web3_client_version() -> spec.RpcRequest:
    return rpc_request.create('web3_clientVersion', [])


def construct_web3_sha3(data: spec.BinaryData) -> spec.RpcRequest:
    return rpc_request.create('web3_sha3', [data])


def construct_net_version() -> spec.RpcRequest:
    return rpc_request.create('net_version', [])


def construct_net_peer_count() -> spec.RpcRequest:
    return rpc_request.create('net_peerCount', [])


def construct_net_listening() -> spec.RpcRequest:
    return rpc_request.create('net_listening', [])


def construct_eth_protocol_version() -> spec.RpcRequest:
    return rpc_request.create('eth_protocolVersion', [])


def construct_eth_syncing() -> spec.RpcRequest:
    return rpc_request.create('eth_syncing', [])


def construct_eth_chain_id() -> spec.RpcRequest:
    return rpc_request.create('eth_chainId', [])
