from ... import binary_utils
from .. import rpc_backends
from .. import rpc_crud


def construct_eth_gas_price():
    return rpc_crud.construct_rpc_call('eth_gasPrice', [])


def construct_eth_accounts():
    return rpc_crud.construct_rpc_call('eth_accounts', [])


def construct_eth_sign(address, message):
    return rpc_crud.construct_rpc_call('eth_sign', [address, message])


def construct_eth_sign_transaction(
    from_address,
    data,
    to_address=None,
    gas=None,
    gas_price=None,
    value=None,
    nonce=None,
):

    parameters = {
        'from': from_address,
        'to': to_address,
        'gas': gas,
        'gasPrice': gas_price,
        'value': value,
        'data': data,
        'nonce': nonce,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    return rpc_crud.construct_rpc_call('eth_signTransaction', [parameters])


def construct_eth_send_transaction(
    from_address,
    data,
    to_address=None,
    gas=None,
    gas_price=None,
    value=None,
    nonce=None,
):
    parameters = {
        'from': from_address,
        'to': to_address,
        'gas': gas,
        'gasPrice': gas_price,
        'value': value,
        'data': data,
        'nonce': nonce,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    return rpc_crud.construct_rpc_call('eth_sendTransaction', [parameters])


def construct_eth_send_raw_transaction(data):
    return rpc_crud.construct_rpc_call('eth_sendRawTransaction', [data])

