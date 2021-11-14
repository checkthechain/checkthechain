from ... import binary_utils
from .. import rpc_crud
from .. import rpc_spec


def digest_eth_new_filter(response, decode_response=False):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_new_block_filter(response, decode_response=False):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_new_pending_transaction_filter(response, decode_response=False):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_uninstall_filter(response, decode_response=False):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_filter_changes(
    response,
    decode_response=True,
    snake_case_response=True,
    include_removed=False,
):
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
            rpc_crud.decode_rpc_map(subresponse, rpc_spec.rpc_log_quantities)
            for subresponse in response
        ]

    if (
        snake_case_response
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            rpc_crud.rpc_keys_to_snake_case(subresponse)
            for subresponse in response
        ]

    return response


def digest_eth_get_filter_logs(
    response,
    decode_response=True,
    snake_case_response=True,
    include_removed=False,
):

    if not include_removed:
        response = [
            subresponse
            for subresponse in response
            if not subresponse['removed']
        ]

    if decode_response and len(response) > 0 and isinstance(response[0], dict):
        response = [
            rpc_crud.decode_rpc_map(subresponse, rpc_spec.rpc_log_quantities)
            for subresponse in response
        ]

    if (
        snake_case_response
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            rpc_crud.rpc_keys_to_snake_case(subresponse)
            for subresponse in response
        ]

    return response


def digest_eth_get_logs(
    response,
    decode_response=True,
    snake_case_response=True,
    include_removed=False,
):
    if not include_removed:
        response = [
            subresponse
            for subresponse in response
            if not subresponse['removed']
        ]

    if decode_response and len(response) > 0 and isinstance(response[0], dict):
        response = [
            rpc_crud.decode_rpc_map(subresponse, rpc_spec.rpc_log_quantities)
            for subresponse in response
        ]

    if (
        snake_case_response
        and len(response) > 0
        and isinstance(response[0], dict)
    ):
        response = [
            rpc_crud.rpc_keys_to_snake_case(subresponse)
            for subresponse in response
        ]

    return response

