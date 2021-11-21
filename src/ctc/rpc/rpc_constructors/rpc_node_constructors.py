from .. import rpc_request


def construct_web3_client_version():
    return rpc_request.create('web3_clientVersion', [])


def construct_web3_sha3(data):
    return rpc_request.create('web3_sha3', [data])


def construct_net_version():
    return rpc_request.create('net_version', [])


def construct_net_peer_count():
    return rpc_request.create('net_peerCount', [])


def construct_net_listening():
    return rpc_request.create('net_listening', [])


def construct_eth_protocol_version():
    return rpc_request.create('eth_protocolVersion', [])


def construct_eth_syncing():
    return rpc_request.create('eth_syncing', [])

