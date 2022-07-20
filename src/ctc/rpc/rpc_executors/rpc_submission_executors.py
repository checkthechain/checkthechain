from __future__ import annotations

from ctc import spec

from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_eth_gas_price(
    *, provider: spec.ProviderReference = None, decode_response: bool = True
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_gas_price()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_gas_price(
        response=response,
        decode_response=decode_response,
    )


async def async_eth_accounts(
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_accounts()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_accounts(response=response)


async def async_eth_sign(
    address: spec.Address,
    message: str,
    *,
    provider: spec.ProviderReference = None,
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_sign(
        address=address,
        message=message,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_sign(response=response)


async def async_eth_sign_transaction(
    from_address: spec.Address,
    data: str,
    *,
    to_address: spec.Address | None = None,
    gas: int | None = None,
    gas_price: int | None = None,
    value: int | None = None,
    nonce: str | None = None,
    provider: spec.ProviderReference = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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
    from_address: spec.Address,
    data: str,
    *,
    to_address: spec.Address | None = None,
    gas: int | None = None,
    gas_price: int | None = None,
    value: int | None = None,
    nonce: str | None = None,
    provider: spec.ProviderReference = None,
    snake_case_response: bool = True,
) -> spec.RpcSingularResponse:
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


async def async_eth_send_raw_transaction(
    data: str, *, provider: spec.ProviderReference = None
) -> spec.RpcSingularResponse:
    request = rpc_constructors.construct_eth_send_raw_transaction(data=data)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_eth_send_raw_transaction(response=response)
