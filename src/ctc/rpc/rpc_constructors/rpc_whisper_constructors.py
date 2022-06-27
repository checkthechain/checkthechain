from __future__ import annotations

import typing

from ctc import spec
from .. import rpc_request


def construct_shh_version() -> spec.RpcRequest:
    return rpc_request.create('shh_version', [])


def construct_shh_post(
    from_address: spec.BinaryData,
    to_address: spec.BinaryData,
    *,
    topics: list[spec.BinaryData],
    payload: spec.BinaryData,
    priority: spec.BinaryData,
    ttl: spec.BinaryData,
) -> spec.RpcRequest:
    data: dict[str, typing.Any] = {
        'from': from_address,
        'to': to_address,
        'topics': topics,
        'payload': payload,
        'priority': priority,
        'ttl': ttl,
    }
    data = {k: v for k, v in data.items() if v is not None}
    return rpc_request.create('shh_new_filter', [data])


def construct_shh_new_identity() -> spec.RpcRequest:
    return rpc_request.create('ssh_new_version', [])


def construct_shh_has_identity(data: spec.BinaryData) -> spec.RpcRequest:
    return rpc_request.create('shh_has_identity', [data])


def construct_shh_new_group() -> spec.RpcRequest:
    return rpc_request.create('shh_new_group', [])


def construct_shh_add_to_group(data: spec.BinaryData) -> spec.RpcRequest:
    return rpc_request.create('shh_add_to_group', [data])


def construct_shh_new_filter(
    to_address: spec.BinaryData, topics: typing.Sequence[spec.BinaryData]
) -> spec.RpcRequest:
    payload = {
        'to': to_address,
        'topics': topics,
    }
    return rpc_request.create('shh_new_filter', [payload])


def construct_shh_uninstall_filter(
    filter_id: spec.BinaryData,
) -> spec.RpcRequest:
    return rpc_request.create('shh_uninstall_filter', [filter_id])


def construct_shh_get_filter_changes(
    filter_id: spec.BinaryData,
) -> spec.RpcRequest:
    return rpc_request.create('shh_get_filter_changes', [filter_id])


def construct_shh_get_messages(filter_id: spec.BinaryData) -> spec.RpcRequest:
    return rpc_request.create('shh_get_messages', [filter_id])
