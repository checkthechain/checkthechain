from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_block_number(provider=None, decode_response=True):
    request = rpc_constructors.construct_eth_block_number()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_block_number(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_block_by_hash(
    block_hash,
    include_full_transactions=False,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_get_block_by_hash(
        block_hash=block_hash,
        include_full_transactions=include_full_transactions,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_block_by_hash(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_block_by_number(
    block_number,
    include_full_transactions=True,
    decode_response=True,
    provider=None,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_get_block_by_number(
        block_number=block_number,
        include_full_transactions=include_full_transactions,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_block_by_number(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_uncle_count_by_block_hash(
    block_hash, provider=None, decode_response=True
):
    request = rpc_constructors.construct_eth_get_uncle_count_by_block_hash(
        block_hash=block_hash,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_uncle_count_by_block_hash(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_uncle_count_by_block_number(
    block_number, provider=None, decode_response=True
):
    request = rpc_constructors.construct_eth_get_uncle_count_by_block_number(
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_uncle_count_by_block_number(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_uncle_by_block_hash_and_index(
    block_hash,
    uncle_index,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_get_uncle_by_block_hash_and_index(
        block_hash=block_hash,
        uncle_index=uncle_index,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_uncle_by_block_hash_and_index(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_uncle_by_block_number_and_index(
    block_number,
    uncle_index,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = (
        rpc_constructors.construct_eth_get_uncle_by_block_number_and_index(
            block_number=block_number,
            uncle_index=uncle_index,
        )
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_uncle_by_block_number_and_index(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )

