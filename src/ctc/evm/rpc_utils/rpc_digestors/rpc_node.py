from ... import binary_utils
from .. import rpc_crud


def digest_web3_client_version(response):
    return response


def digest_web3_sha3(response):
    return response


def digest_net_version(response):
    return response


def digest_net_peer_count(response):
    return response


def digest_net_listening(response):
    return response


def digest_eth_protocol_version(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_syncing(response, snake_case_response=True):
    if snake_case_response:
        if isinstance(response, dict):
            response = rpc_crud.rpc_keys_to_snake_case(response)
    return response

