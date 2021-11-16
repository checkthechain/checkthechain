from ... import binary_utils
from .. import rpc_crud
from .. import rpc_spec


def digest_eth_block_number(response, decode_response):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_block_by_hash(
    response, decode_response=True, snake_case_response=True
):
    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_crud.decode_rpc_map(response, quantities=quantities)

    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)

    return response


def digest_eth_get_block_by_number(
    response,
    future,
    decode_response=True,
    snake_case_response=True,
):

    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_crud.decode_rpc_map(response, quantities=quantities)

    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)

    include_full_transactions = len(
        response['transactions']
    ) > 0 and isinstance(response['transactions'][0], dict)
    if include_full_transactions and (decode_response or snake_case_response):

        transaction_quantities = rpc_spec.rpc_transaction_quantities
        new_transactions = []
        for transaction in response['transactions']:

            new_transaction = transaction

            if decode_response:
                new_transaction = rpc_crud.decode_rpc_map(
                    new_transaction, quantities=transaction_quantities
                )

            if snake_case_response:
                new_transaction = rpc_crud.rpc_keys_to_snake_case(
                    new_transaction
                )
            new_transactions.append(new_transaction)

        response['transactions'] = new_transactions

    return response


def digest_eth_get_uncle_count_by_block_hash(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_uncle_count_by_block_number(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_uncle_by_block_hash_and_index(
    response,
    decode_response=True,
    snake_case_response=True,
):
    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_crud.decode_rpc_map(response, quantities=quantities)

    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)

    return response


def digest_eth_get_uncle_by_block_number_and_index(
    response,
    decode_response=True,
    snake_case_response=True,
):
    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_crud.decode_rpc_map(response, quantities=quantities)

    if snake_case_response:
        response = rpc_crud.rpc_keys_to_snake_case(response)

    return response

