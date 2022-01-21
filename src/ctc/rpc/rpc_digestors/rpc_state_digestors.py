import typing

from ctc import spec
from ctc import binary


def digest_eth_call(
    response: spec.RpcSingularResponse,
    function_abi: spec.FunctionABI,
    decode_response: bool = True,
    delist_single_outputs: bool = True,
    package_named_outputs: bool = False,
    fill_empty: bool = False,
    empty_token: typing.Any = None,
) -> spec.RpcSingularResponse:

    if decode_response:

        if (fill_empty or empty_token is not None) and response == '0x':
            response = empty_token

        else:
            response = binary.decode_function_output(
                encoded_output=response,
                delist_single_outputs=delist_single_outputs,
                package_named_outputs=package_named_outputs,
                function_abi=function_abi,
            )

    return response


def digest_eth_estimate_gas(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response


def digest_eth_get_balance(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response


def digest_eth_get_storage_at(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_eth_get_code(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response

