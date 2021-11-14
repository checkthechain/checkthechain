from .. import rpc_crud


def construct_web3_client_version():
    return rpc_crud.construct_rpc_call('web3_clientVersion', [])


def construct_web3_sha3(data):
    return rpc_crud.construct_rpc_call('web3_sha3', [data])


def construct_net_version():
    return rpc_crud.construct_rpc_call('net_version', [])


def construct_net_peer_count():
    return rpc_crud.construct_rpc_call('net_peerCount', [])


def construct_net_listening():
    return rpc_crud.construct_rpc_call('net_listening', [])


def construct_eth_protocol_version():
    return rpc_crud.construct_rpc_call('eth_protocolVersion', [])


def construct_eth_syncing():
    return rpc_crud.construct_rpc_call('eth_syncing', [])

