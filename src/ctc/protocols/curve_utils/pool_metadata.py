from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import curve_spec


async def async_get_pool_addresses(
    pool: spec.Address,
    n_tokens: int | None = None,
    provider: spec.ProviderSpec = None,
) -> list[spec.Address]:
    import asyncio

    if n_tokens is None:
        token_addresses = []
        t = 0
        function_abi: spec.FunctionABI = {
            'name': 'coins',
            'inputs': [{'type': 'uint256'}],
            'outputs': [{'type': 'address'}],
        }
        while True:
            try:
                token_address = await rpc.async_eth_call(
                    to_address=pool,
                    function_abi=function_abi,
                    function_parameters=[t],
                    provider=provider,
                )
                token_addresses.append(token_address)
                t += 1
            except spec.RpcException:
                break
    else:
        function_abi = {
            'name': 'coins',
            'inputs': [{'type': 'uint256'}],
            'outputs': [{'type': 'address'}],
        }
        address_coroutines = [
            rpc.async_eth_call(
                to_address=pool,
                function_abi=function_abi,
                function_parameters=[i],
                provider=provider,
            )
            for i in range(n_tokens)
        ]
        token_addresses = await asyncio.gather(*address_coroutines)

    return token_addresses


async def async_get_token_index(
    token: typing.Union[int, spec.Address, str],
    pool: spec.Address | None = None,
    metadata: curve_spec.CurvePoolMetadata | None = None,
    n_tokens: int | None = None,
    provider: spec.ProviderSpec = None,
) -> int:

    if isinstance(token, int):
        # token already an index
        return token

    elif isinstance(token, str) and token.startswith('0x'):
        # token an address
        if metadata is not None:
            pool_addresses = metadata['token_addresses']
        elif pool is not None:
            pool_addresses = await async_get_pool_addresses(
                pool=pool,
                n_tokens=n_tokens,
                provider=provider,
            )
        else:
            raise Exception('must specify more parameters')
        return pool_addresses.index(token)

    elif isinstance(token, str):
        # token a symbol
        if metadata is not None:
            pool_addresses = metadata['token_addresses']
        elif pool is not None:
            pool_addresses = await async_get_pool_addresses(
                pool=pool,
                n_tokens=n_tokens,
                provider=provider,
            )
        else:
            raise Exception('must specify more parameters')
        token_symbols = await evm.async_get_erc20s_symbols(
            pool_addresses,
            provider=provider,
        )
        return token_symbols.index(token)

    else:
        raise Exception()


async def async_get_pool_metadata(
    pool: spec.Address,
    n_tokens: int | None = None,
    provider: spec.ProviderSpec = None,
) -> curve_spec.CurvePoolMetadata:

    import asyncio

    a_coroutine = rpc.async_eth_call(
        to_address=pool,
        function_name='A',
        function_parameters=[],
        provider=provider,
    )
    a_task = asyncio.create_task(a_coroutine)

    # get addresses
    token_addresses = await async_get_pool_addresses(
        pool,
        n_tokens=n_tokens,
        provider=provider,
    )

    # get additional metadata
    symbol_coroutine = evm.async_get_erc20s_symbols(
        token_addresses,
        provider=provider,
    )
    decimal_coroutine = evm.async_get_erc20s_decimals(
        token_addresses,
        provider=provider,
    )
    symbol_task = asyncio.create_task(symbol_coroutine)
    decimal_task = asyncio.create_task(decimal_coroutine)

    # await results
    token_symbols = await symbol_task
    token_decimals = await decimal_task
    A = await a_task

    return {
        'token_addresses': token_addresses,
        'token_symbols': token_symbols,
        'token_decimals': token_decimals,
        'A': A,
        # fee:
    }

