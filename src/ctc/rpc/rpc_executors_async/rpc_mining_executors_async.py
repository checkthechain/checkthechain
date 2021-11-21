from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_get_work(provider=None):
    request = rpc_constructors.construct_eth_get_work()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_work(response=response)


async def async_eth_submit_work(nonce, pow_hash, digest, provider=None):
    request = rpc_constructors.construct_eth_submit_work(
        nonce=nonce,
        pow_hash=pow_hash,
        digest=digest,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_submit_work(response=response)


async def async_eth_submit_hashrate(hashrate, id, provider=None):
    request = rpc_constructors.construct_eth_submit_hashrate(
        hashrate=hashrate,
        id=id,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_submit_hashrate(response=response)


async def async_eth_coinbase(provider=None):
    request = rpc_constructors.construct_eth_coinbase()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_coinbase(response=response)


async def async_eth_mining(provider=None):
    request = rpc_constructors.construct_eth_mining()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_mining(response=response)


async def async_eth_hashrate(provider=None):
    request = rpc_constructors.construct_eth_hashrate()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_hashrate(response=response)

