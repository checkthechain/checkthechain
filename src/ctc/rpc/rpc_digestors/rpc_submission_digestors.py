from ctc.evm import binary_utils
from .. import rpc_format


def digest_eth_gas_price(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_accounts(response):
    return response


def digest_eth_sign(response):
    return response


def digest_eth_sign_transaction(response, snake_case_response=True):
    if snake_case_response:
        response = rpc_format.rpc_keys_to_snake_case(response)
    return response


def digest_eth_send_transaction(response, snake_case_response=True):
    if snake_case_response:
        response = rpc_format.rpc_keys_to_snake_case(response)
    return response


def digest_eth_send_raw_transaction(response):
    return response

