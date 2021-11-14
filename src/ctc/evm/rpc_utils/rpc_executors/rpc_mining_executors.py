from .. import rpc_backends


def eth_get_work(provider=None):
    return rpc_backends.rpc_call(
        method='eth_getWork',
        parameters=[],
        provider=provider,
    )


def eth_submit_work(nonce, pow_hash, digest, provider=None):
    return rpc_backends.rpc_call(
        method='eth_submitWork',
        parameters=[nonce, pow_hash, digest],
        provider=provider,
    )


def eth_submit_hashrate(hashrate, id, provider=None):
    return rpc_backends.rpc_call(
        method='eth_submitHashrate',
        parameters=[hashrate, id],
        provider=provider,
    )


def eth_coinbase(provider=None):
    return rpc_backends.rpc_call(
        method='eth_coinbase',
        parameters=[],
        provider=provider,
    )


def eth_mining(provider=None):
    return rpc_backends.rpc_call(
        method='eth_mining',
        parameters=[],
        provider=provider,
    )


def eth_hashrate(provider=None):
    return rpc_backends.rpc_call(
        method='eth_hashrate',
        parameters=[],
        provider=provider,
    )

