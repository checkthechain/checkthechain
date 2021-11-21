from .. import rpc_request


def construct_eth_get_work():
    return rpc_request.create('eth_getWork', [])


def construct_eth_submit_work(nonce, pow_hash, digest):
    parameters = [nonce, pow_hash, digest]
    return rpc_request.create('eth_submitWork', parameters)


def construct_eth_submit_hashrate(hashrate, id):
    return rpc_request.create('eth_submitHashrate', [hashrate, id])


def construct_eth_coinbase():
    return rpc_request.create('eth_coinbase', [])


def construct_eth_mining():
    return rpc_request.create('eth_mining', [])


def construct_eth_hashrate():
    return rpc_request.create('eth_hashrate', [])

