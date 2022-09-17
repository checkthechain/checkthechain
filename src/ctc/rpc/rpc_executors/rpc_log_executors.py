from __future__ import annotations

import typing

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_new_filter(
    *,
    address: spec.Address | None = None,
    topics: typing.Sequence[spec.BinaryData] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
    decode_response: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_new_filter(
        address=address,
        topics=topics,
        start_block=start_block,
        end_block=end_block,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_new_filter(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_new_block_filter(
    *, provider: spec.ProviderReference = None, decode_response: bool = False
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_new_block_filter()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_new_block_filter(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_new_pending_transaction_filter(
    *, provider: spec.ProviderReference = None, decode_response: bool = False
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_new_pending_transaction_filter()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_new_pending_transaction_filter(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_uninstall_filter(
    filter_id: spec.GenericBinaryData,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_uninstall_filter(
        filter_id=filter_id
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_uninstall_filter(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_get_filter_changes(
    filter_id: spec.GenericBinaryData,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_filter_changes(
        filter_id=filter_id
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_filter_changes(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
        include_removed=include_removed,
    )


async def async_eth_get_filter_logs(
    filter_id: spec.GenericBinaryData,
    *,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_filter_logs(
        filter_id=filter_id
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_filter_logs(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
        include_removed=include_removed,
    )


async def async_eth_get_logs(
    *,
    address: spec.BinaryData | None = None,
    topics: typing.Sequence[spec.BinaryData] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    block_hash: spec.BinaryData | None = None,
    provider: spec.ProviderReference = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:

    request = rpc_constructors.construct_eth_get_logs(
        address=address,
        topics=topics,
        start_block=start_block,
        end_block=end_block,
        block_hash=block_hash,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_get_logs(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
        include_removed=include_removed,
    )
