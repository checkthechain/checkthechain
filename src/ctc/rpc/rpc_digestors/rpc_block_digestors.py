from __future__ import annotations

from ctc import evm
from ctc import spec
from .. import rpc_format
from .. import rpc_spec


def digest_eth_block_number(
    response: spec.RpcSingularResponse, *, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_get_block_by_hash(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_format.decode_response(response, quantities=quantities)

    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)

    return response


def digest_eth_get_block_by_number(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:

    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_format.decode_response(response, quantities=quantities)

    response['totalDifficulty'] = str(response['totalDifficulty'])

    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)

    include_full_transactions = len(
        response['transactions']
    ) > 0 and isinstance(response['transactions'][0], dict)
    if include_full_transactions and (decode_response or snake_case_response):

        transaction_quantities = rpc_spec.rpc_transaction_quantities
        new_transactions = []
        for transaction in response['transactions']:

            new_transaction = transaction

            if decode_response:
                new_transaction = rpc_format.decode_response(
                    new_transaction, quantities=transaction_quantities
                )

            if snake_case_response:
                new_transaction = rpc_format.keys_to_snake_case(new_transaction)
            new_transactions.append(new_transaction)

        response['transactions'] = new_transactions

    return response


def digest_eth_get_uncle_count_by_block_hash(
    response: spec.RpcSingularResponse, *, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_get_uncle_count_by_block_number(
    response: spec.RpcSingularResponse, *, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = evm.binary_convert(response, 'integer')
    return response


def digest_eth_get_uncle_by_block_hash_and_index(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_format.decode_response(response, quantities=quantities)

    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)

    return response


def digest_eth_get_uncle_by_block_number_and_index(
    response: spec.RpcSingularResponse,
    *,
    decode_response: bool = True,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
    if decode_response:
        quantities = rpc_spec.rpc_block_quantities
        response = rpc_format.decode_response(response, quantities=quantities)

    if snake_case_response:
        response = rpc_format.keys_to_snake_case(response)

    return response
