from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_block_number(
    *, provider: spec.ProviderReference = None, decode_response: bool = True
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_block_number()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_block_number(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_block_by_hash(
    block_hash: str,
    *,
    include_full_transactions: bool = False,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    block_number: spec.StandardBlockNumber,
    *,
    include_full_transactions: bool = False,
    decode_response: bool = True,
    provider: spec.ProviderReference = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    block_hash: str,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_uncle_count_by_block_hash(
        block_hash=block_hash,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_uncle_count_by_block_hash(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_uncle_count_by_block_number(
    block_number: spec.StandardBlockNumber,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_uncle_count_by_block_number(
        block_number=block_number,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_uncle_count_by_block_number(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_uncle_by_block_hash_and_index(
    block_hash: str,
    uncle_index: str,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    block_number: spec.StandardBlockNumber,
    uncle_index: str,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
