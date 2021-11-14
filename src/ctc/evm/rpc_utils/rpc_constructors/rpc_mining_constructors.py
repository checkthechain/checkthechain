from .. import rpc_crud


def construct_eth_get_work():
    return rpc_crud.construct_rpc_call('eth_getWork', [])


def construct_eth_submit_work(nonce, pow_hash, digest):
    parameters = [nonce, pow_hash, digest]
    return rpc_crud.construct_rpc_call('eth_submitWork', parameters)


def construct_eth_submit_hashrate(hashrate, id):
    return rpc_crud.construct_rpc_call('eth_submitHashrate', [hashrate, id])


def construct_eth_coinbase():
    return rpc_crud.construct_rpc_call('eth_coinbase', [])


def construct_eth_mining():
    return rpc_crud.construct_rpc_call('eth_mining', [])


def construct_eth_hashrate():
    return rpc_crud.construct_rpc_call('eth_hashrate', [])

