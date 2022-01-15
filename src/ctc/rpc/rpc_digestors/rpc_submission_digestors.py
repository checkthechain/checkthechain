from ctc import spec
from ctc import binary
from .. import rpc_format


def digest_eth_gas_price(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response


def digest_eth_accounts(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_eth_sign(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_eth_sign_transaction(
    response: spec.RpcSingularResponse, snake_case_response: bool = True
) -> spec.RpcSingularResponse:
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_send_transaction(
    response: spec.RpcSingularResponse, snake_case_response: bool = True
) -> spec.RpcSingularResponse:
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_send_raw_transaction(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response

