from ctc import spec
from ctc import binary
from .. import rpc_format


def digest_web3_client_version(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_web3_sha3(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_net_version(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_net_peer_count(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_net_listening(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_eth_protocol_version(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary.convert(response, 'integer')
    return response


def digest_eth_syncing(
    response: spec.RpcSingularResponse, snake_case_response: bool = True
) -> spec.RpcSingularResponse:
    if snake_case_response:
        if isinstance(response, dict):
            response = rpc_format.keys_to_snake_case(response)
    return response

