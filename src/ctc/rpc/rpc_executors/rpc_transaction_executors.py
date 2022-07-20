from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_get_transaction_count(
    from_address: spec.Address,
    *,
    block_number: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    if block_number is None:
        block_number = 'latest'
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
    transaction_hash: str,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    block_hash: spec.BinaryData,
    transaction_index: spec.BinaryData,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    block_number: spec.BlockNumberReference,
    transaction_index: spec.BinaryData,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    transaction_hash: str,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    block_hash: str,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = (
        rpc_constructors.construct_eth_get_block_transaction_count_by_hash(
            block_hash=block_hash,
        )
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_block_transaction_count_by_hash(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_block_transaction_count_by_number(
    block_number: spec.BlockNumberReference,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = (
        rpc_constructors.construct_eth_get_block_transaction_count_by_number(
            block_number=block_number,
        )
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_block_transaction_count_by_number(
        response=response,
        decode_response=decode_response,
    )
