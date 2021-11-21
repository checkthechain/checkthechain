from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_web3_client_version(provider=None):
    request = rpc_constructors.construct_web3_client_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_web3_client_version(response=response)


async def async_web3_sha3(data, provider=None):
    request = rpc_constructors.construct_web3_sha3(data)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_web3_sha3(response=response)


async def async_net_version(provider=None):
    request = rpc_constructors.construct_net_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_net_version(response=response)


async def async_net_peer_count(provider=None):
    request = rpc_constructors.construct_net_peer_count()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_net_peer_count(response=response)


async def async_net_listening(provider=None):
    request = rpc_constructors.construct_net_listening()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_net_listening(response=response)


async def async_eth_protocol_version(provider=None, decode_response=True):
    request = rpc_constructors.construct_eth_protocol_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_protocol_version(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_syncing(provider=None, snake_case_response=True):
    request = rpc_constructors.construct_eth_syncing()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_syncing(
        response=response,
        snake_case_response=snake_case_response,
    )

