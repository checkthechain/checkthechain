from ... import binary_utils
from .. import rpc_backends
from .. import rpc_crud


def web3_client_version(provider=None):
    return rpc_backends.rpc_call(
        method='web3_clientVersion',
        parameters=[],
        provider=provider,
    )


def web3_sha3(data, provider=None):
    return rpc_backends.rpc_call(
        method='web3_sha3',
        parameters=[data],
        provider=provider,
    )


def net_version(provider=None):
    return rpc_backends.rpc_call(
        method='net_version',
        parameters=[],
        provider=provider,
    )


def net_peer_count(provider=None):
    return rpc_backends.rpc_call(
        method='net_peerCount',
        parameters=[],
        provider=provider,
    )


def net_listening(provider=None):
    return rpc_backends.rpc_call(
        method='net_listening',
        parameters=[],
        provider=provider,
    )


def eth_protocol_version(provider=None, decode_result=True):
    result = rpc_backends.rpc_call(
        method='eth_protocolVersion',
        parameters=[],
        provider=provider,
    )
    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')
    return result


def eth_syncing(provider=None, snake_case_result=True):
    result = rpc_backends.rpc_call(
        method='eth_syncing',
        parameters=[],
        provider=provider,
    )

    if snake_case_result:
        if isinstance(result, dict):
            result = rpc_crud.rpc_keys_to_snake_case(result)

    return result

