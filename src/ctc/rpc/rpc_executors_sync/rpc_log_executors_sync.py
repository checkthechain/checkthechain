from __future__ import annotations

import typing

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


def sync_eth_new_filter(
    *,
    address: spec.Address | None = None,
    topics: typing.Sequence[spec.BinaryData | None] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
    decode_response: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_new_filter(
        address=address,
        topics=topics,
        start_block=start_block,
        end_block=end_block,
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_new_filter(
        response=response,
        decode_response=decode_response,
    )


def sync_eth_new_block_filter(
    *, context: spec.Context = None, decode_response: bool = False
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_new_block_filter()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_new_block_filter(
        response=response,
        decode_response=decode_response,
    )


def sync_eth_new_pending_transaction_filter(
    *, context: spec.Context = None, decode_response: bool = False
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_new_pending_transaction_filter()
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_new_pending_transaction_filter(
        response=response,
        decode_response=decode_response,
    )


def sync_eth_uninstall_filter(
    filter_id: spec.GenericBinaryData,
    *,
    context: spec.Context = None,
    decode_response: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_uninstall_filter(
        filter_id=filter_id
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_uninstall_filter(
        response=response,
        decode_response=decode_response,
    )


def sync_eth_get_filter_changes(
    filter_id: spec.GenericBinaryData,
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_filter_changes(
        filter_id=filter_id
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_get_filter_changes(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
        include_removed=include_removed,
    )


def sync_eth_get_filter_logs(
    filter_id: spec.GenericBinaryData,
    *,
    context: spec.Context = None,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_get_filter_logs(
        filter_id=filter_id
    )
    response = rpc_request.sync_send(request, context=context)
    return rpc_digestors.digest_eth_get_filter_logs(
        response=response,
        decode_response=decode_response,
        snake_case_response=snake_case_response,
        include_removed=include_removed,
    )


def sync_eth_get_logs(
    *,
    address: spec.BinaryData | None = None,
    topics: typing.Sequence[spec.BinaryData | None] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    block_hash: spec.BinaryData | None = None,
    context: spec.Context = None,
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

    import sys

    if (sys.version_info.major, sys.version_info.minor) >= (3, 8):
        from ctc.rpc.rpc_decoders import log_decoder

        raw_response = rpc_request.sync_send(
            request,
            context=context,
            raw_output=True,
        )
        return log_decoder.decode_logs(
            raw_response,
            include_removed=include_removed,
        )

    else:
        response = rpc_request.sync_send(request, context=context)
        logs = rpc_digestors.digest_eth_get_logs(
            response=response,
            decode_response=decode_response,
            snake_case_response=snake_case_response,
            include_removed=include_removed,
        )
        return [
            (
                log['block_number'],
                log['transaction_index'],
                log['log_index'],
                log['transaction_hash'],
                log['address'],
                tuple(log['topics']),
                log['data'],
                log['block_hash'],
            )
            for log in logs
        ]

