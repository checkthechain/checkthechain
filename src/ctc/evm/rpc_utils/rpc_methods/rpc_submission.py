from ... import binary_utils
from .. import rpc_backends
from .. import rpc_crud


def eth_gas_price(provider=None, decode_result=True):
    result = rpc_backends.rpc_call(
        method='eth_gasPrice',
        parameters=[],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_accounts(provider=None):
    return rpc_backends.rpc_call(
        method='eth_accounts',
        parameters=[],
        provider=provider,
    )


def eth_sign(address, message, provider=None):
    return rpc_backends.rpc_call(
        method='eth_sign',
        parameters=[address, message],
        provider=provider,
    )


def eth_sign_transaction(
    from_address,
    data,
    to_address=None,
    gas=None,
    gas_price=None,
    value=None,
    nonce=None,
    provider=None,
    snake_case_result=True,
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

    result = rpc_backends.rpc_call(
        method='eth_signTransaction',
        parameters=[parameters],
        provider=provider,
    )

    if snake_case_result:
        result = rpc_crud.rpc_keys_to_snake_case(result)

    return result


def eth_send_transaction(
    from_address,
    data,
    to_address=None,
    gas=None,
    gas_price=None,
    value=None,
    nonce=None,
    provider=None,
    snake_case_result=True,
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

    result = rpc_backends.rpc_call(
        method='eth_sendTransaction',
        parameters=[parameters],
        provider=provider,
    )

    if snake_case_result:
        result = rpc_crud.rpc_keys_to_snake_case(result)

    return result


def eth_send_raw_transaction(data, provider=None):
    return rpc_backends.rpc_call(
        method='eth_sendRawTransaction',
        parameters=[data],
        provider=provider,
    )

