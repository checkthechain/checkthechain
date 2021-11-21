from ctc import spec
from ctc.evm import binary_utils
from .. import rpc_format


def digest_eth_gas_price(
    response: spec.RpcResponse, decode_response: bool = True
) -> spec.RpcResponse:
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_accounts(response: spec.RpcResponse) -> spec.RpcResponse:
    return response


def digest_eth_sign(response: spec.RpcResponse) -> spec.RpcResponse:
    return response


def digest_eth_sign_transaction(
    response: spec.RpcResponse, snake_case_response: bool = True
) -> spec.RpcResponse:
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_send_transaction(
    response: spec.RpcResponse, snake_case_response: bool = True
) -> spec.RpcResponse:
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_send_raw_transaction(
    response: spec.RpcResponse,
) -> spec.RpcResponse:
    return response

