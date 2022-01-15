from ctc import spec
from ctc import binary
from .. import rpc_format
from .. import rpc_spec


def digest_eth_get_transaction_count(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response


def digest_eth_get_transaction_by_hash(
    response: spec.RpcSingularResponse,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_transaction_quantities
        response = rpc_format.decode_response(response, quantities)
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_get_transaction_by_block_hash_and_index(
    response: spec.RpcSingularResponse,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_transaction_quantities
        response = rpc_format.decode_response(response, quantities)
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_get_transaction_by_block_number_and_index(
    response: spec.RpcSingularResponse,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_transaction_quantities
        response = rpc_format.decode_response(response, quantities)
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_get_transaction_receipt(
    response: spec.RpcSingularResponse,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_transaction_receipt_quantities
        response = rpc_format.decode_response(response, quantities)
    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)
    return response


def digest_eth_get_block_transaction_count_by_hash(
    response: spec.RpcSingularResponse,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response


def digest_eth_get_block_transaction_count_by_number(
    response: spec.RpcSingularResponse,
    decode_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response

