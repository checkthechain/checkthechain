from __future__ import annotations

import typing

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


def sync_shh_version(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_version()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_version(
        response=response,
    )


def sync_shh_post(
    *,
    from_address: spec.BinaryData,
    to_address: spec.BinaryData,
    topics: list[spec.BinaryData],
    payload: spec.BinaryData,
    priority: spec.BinaryData,
    ttl: spec.BinaryData,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_post(
        from_address=from_address,
        to_address=to_address,
        topics=topics,
        payload=payload,
        priority=priority,
        ttl=ttl,
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_post(
        response=response,
    )


def sync_shh_new_identity(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_new_identity()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_new_identity(response=response)


def sync_shh_has_identity(
    data: spec.BinaryData,
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_has_identity(data=data)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_has_identity(response=response)


def sync_shh_new_group(
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_new_group()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_new_group(response=response)


def sync_shh_add_to_group(
    data: spec.BinaryData, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_add_to_group(data=data)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_add_to_group(response=response)


def sync_shh_new_filter(
    to_address: spec.Address,
    topics: typing.Sequence[spec.BinaryData],
    *,
    context: spec.Context = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_new_filter(
        to_address=to_address, topics=topics
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_new_filter(response=response)


def sync_shh_uninstall_filter(
    filter_id: spec.BinaryData, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_uninstall_filter(
        filter_id=filter_id
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_uninstall_filter(
        response=response,
    )


def sync_shh_get_filter_changes(
    filter_id: spec.BinaryData, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_get_filter_changes(
        filter_id=filter_id,
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_get_filter_changes(
        response=response,
    )


def sync_shh_get_messages(
    filter_id: spec.BinaryData, *, context: spec.Context = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_shh_get_messages(filter_id=filter_id)
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_shh_get_messages(
        response=response,
    )

