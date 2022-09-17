from __future__ import annotations

from ctc import evm
from ctc import spec
from .. import rpc_format
from .. import rpc_spec


def digest_eth_new_filter(
    response: spec.RpcSingularResponse, *, decode_response: bool = False
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_new_block_filter(
    response: spec.RpcSingularResponse, *, decode_response: bool = False
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_new_pending_transaction_filter(
    response: spec.RpcSingularResponse, *, decode_response: bool = False
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_uninstall_filter(
    response: spec.RpcSingularResponse, *, decode_response: bool = False
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_get_filter_changes(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:
    if (
        not include_removed
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            subresponse
            for subresponse in response
            if not subresponse['removed']
        ]

    if decode_response and len(response) > 0 and isinstance(response[0], dict):
        response = [
            rpc_format.decode_response(subresponse, rpc_spec.rpc_log_quantities)
            for subresponse in response
        ]

    if (
        snake_case_response
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            rpc_format.keys_to_snake_case(subresponse)
            for subresponse in response
        ]

    return response


def digest_eth_get_filter_logs(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:

    if not include_removed:
        response = [
            subresponse
            for subresponse in response
            if not subresponse['removed']
        ]

    if decode_response and len(response) > 0 and isinstance(response[0], dict):
        response = [
            rpc_format.decode_response(subresponse, rpc_spec.rpc_log_quantities)
            for subresponse in response
        ]

    if (
        snake_case_response
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            rpc_format.keys_to_snake_case(subresponse)
            for subresponse in response
        ]

    return response


def digest_eth_get_logs(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
    include_removed: bool = False,
) -> spec.RpcSingularResponse:
    if not include_removed:
        response = [
            subresponse
            for subresponse in response
            if not subresponse['removed']
        ]

    if decode_response and len(response) > 0 and isinstance(response[0], dict):
        response = [
            rpc_format.decode_response(subresponse, rpc_spec.rpc_log_quantities)
            for subresponse in response
        ]

    if (
        snake_case_response
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            rpc_format.keys_to_snake_case(subresponse)
            for subresponse in response
        ]

    return response
