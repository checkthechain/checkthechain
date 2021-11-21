from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_gas_price(provider=None, decode_response=True):
    request = rpc_constructors.construct_eth_gas_price()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_gas_price(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_accounts(provider=None):
    request = rpc_constructors.construct_eth_accounts()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_accounts(response=response)


async def async_eth_sign(address, message, provider=None):
    request = rpc_constructors.construct_eth_sign(
        address=address,
        message=message,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_sign(response=response)


async def async_eth_sign_transaction(
    from_address,
    data,
    to_address=None,
    gas=None,
    gas_price=None,
    value=None,
    nonce=None,
    provider=None,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_sign_transaction(
        from_address=from_address,
        data=data,
        to_address=to_address,
        gas=gas,
        gas_price=gas_price,
        value=value,
        nonce=nonce,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_sign_transaction(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_eth_send_transaction(
    from_address,
    data,
    to_address=None,
    gas=None,
    gas_price=None,
    value=None,
    nonce=None,
    provider=None,
    snake_case_response=True,
):
    request = rpc_constructors.construct_eth_send_transaction(
        from_address=from_address,
        data=data,
        to_address=to_address,
        gas=gas,
        gas_price=gas_price,
        value=value,
        nonce=nonce,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_send_transaction(
        response=response,
        snake_case_response=snake_case_response,
    )


async def async_eth_send_raw_transaction(data, provider=None):
    request = rpc_constructors.construct_eth_send_raw_transaction()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_send_raw_transaction(response=response)

