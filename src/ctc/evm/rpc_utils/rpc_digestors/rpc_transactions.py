from ... import binary_utils
from .. import rpc_backends
from .. import rpc_crud
from .. import rpc_spec


def digest_eth_get_transaction_count(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_transaction_by_hash(
    response,
    decode_response=True,
    snake_case_response=True,
):
    if decode_response:
        quantities = rpc_spec.rpc_transaction_quantities
        response = rpc_crud.decode_rpc_map(response, quantities)
    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)
    return response


def digest_eth_get_transaction_by_block_hash_and_index(
    response,
    decode_response=True,
    snake_case_response=True,
):
    if decode_response:
        quantities = rpc_spec.rpc_transaction_quantities
        response = rpc_crud.decode_rpc_map(response, quantities)
    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)
    return response


def digest_eth_get_transaction_by_block_number_and_index(
    response,
    decode_response=True,
    snake_case_response=True,
):
    if decode_response:
        quantities = rpc_spec.rpc_transaction_quantities
        response = rpc_crud.decode_rpc_map(response, quantities)
    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)
    return response


def digest_eth_get_transaction_receipt(
    response,
    decode_response=True,
    snake_case_response=True,
):
    if decode_response:
        quantities = rpc_spec.rpc_transaction_receipt_quantities
        response = rpc_crud.decode_rpc_map(response, quantities)
    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)
    return response


def digest_eth_get_block_transaction_count_by_hash(
    response,
    decode_response=True,
):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_block_transaction_count_by_number(
    response,
    decode_response=True,
):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response

