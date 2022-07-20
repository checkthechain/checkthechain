from __future__ import annotations

import typing

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_shh_version(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_version(
        response=response,
    )


async def async_shh_post(
    *,
    from_address: spec.BinaryData,
    to_address: spec.BinaryData,
    topics: list[spec.BinaryData],
    payload: spec.BinaryData,
    priority: spec.BinaryData,
    ttl: spec.BinaryData,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_post(
        from_address=from_address,
        to_address=to_address,
        topics=topics,
        payload=payload,
        priority=priority,
        ttl=ttl,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_post(
        response=response,
    )


async def async_shh_new_identity(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_new_identity()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_new_identity(response=response)


async def async_shh_has_identity(
    data: spec.BinaryData,
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_has_identity(data=data)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_has_identity(response=response)


async def async_shh_new_group(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_new_group()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_new_group(response=response)


async def async_shh_add_to_group(
    data: spec.BinaryData, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_add_to_group(data=data)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_add_to_group(response=response)


async def async_shh_new_filter(
    to_address: spec.Address,
    topics: typing.Sequence[spec.BinaryData],
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_new_filter(
        to_address=to_address, topics=topics
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_new_filter(response=response)


async def async_shh_uninstall_filter(
    filter_id: spec.BinaryData, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_uninstall_filter(
        filter_id=filter_id
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_uninstall_filter(
        response=response,
    )


async def async_shh_get_filter_changes(
    filter_id: spec.BinaryData, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_get_filter_changes(
        filter_id=filter_id,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_get_filter_changes(
        response=response,
    )


async def async_shh_get_messages(
    filter_id: spec.BinaryData, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_get_messages(filter_id=filter_id)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_get_messages(
        response=response,
    )
