from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_get_transaction_count(
    from_address,
    block_number='latest',
    provider=None,
    decode_response=True,
):
    request = rpc_constructors.construct_eth_get_transaction_count(
        from_address=from_address,
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_transaction_count(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_transaction_by_hash(
    transaction_hash,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_get_transaction_by_hash(
        transaction_hash=transaction_hash
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_transaction_by_hash(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_transaction_by_block_hash_and_index(
    block_hash,
    transaction_index,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = (
        rpc_constructors.construct_eth_get_transaction_by_block_hash_and_index(
            block_hash=block_hash,
            transaction_index=transaction_index,
        )
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_transaction_by_block_hash_and_index(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_transaction_by_block_number_and_index(
    block_number,
    transaction_index,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_get_transaction_by_block_number_and_index(
        block_number=block_number,
        transaction_index=transaction_index,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_transaction_by_block_number_and_index(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_transaction_receipt(
    transaction_hash,
    provider=None,
    decode_response=True,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_get_transaction_receipt(
        transaction_hash=transaction_hash,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_transaction_receipt(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
    )


async def async_eth_get_block_transaction_count_by_hash(
    block_hash,
    provider=None,
    decode_response=True,
):
    request = rpc_constructors.construct_eth_get_block_transaction_count_by_hash(
        block_hash=block_hash,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_block_transaction_count_by_hash(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_block_transaction_count_by_number(
    block_number,
    provider=None,
    decode_response=True,
):
    request = rpc_constructors.construct_eth_get_block_transaction_count_by_number(
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_block_transaction_count_by_number(
        response=response,
        decode_response=decode_response,
    )

