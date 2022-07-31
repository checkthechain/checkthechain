from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import curve_spec


async def async_get_pool_tokens(
    pool: spec.Address,
    *,
    n_tokens: int | None = None,
    provider: spec.ProviderReference = None,
) -> list[spec.Address]:
    import asyncio

    old_pools = {
        '0x79a8c46dea5ada233abaffd40f3a0a2b1e5a4f27',
        '0xa2b47e3d5c44877cca798226b7b8118f9bfb7a56',
        '0x06364f10b501e868329afbc005b3492902d6c763',
        '0x93054188d876f558f4a66b2ef1d97d16edf0895b',
        '0x7fc77b5c7614e1533320ea6ddc2eb61fa00a9714',
        '0xa5407eae9ba41422680e2e00537571bcc53efbfd',
        '0x52ea46506b9cc5ef470c5bf89f17dc28bb35d85c',
        '0x45f783cce6b7ff23b2ab2d70e416cdb7d6055f51',
    }
    if pool in old_pools:
        function_abi: spec.FunctionABI = {
            'name': 'coins',
            'inputs': [{'type': 'int128'}],
            'outputs': [{'type': 'address'}],
        }
    else:
        function_abi = {
            'name': 'coins',
            'inputs': [{'type': 'uint256'}],
            'outputs': [{'type': 'address'}],
        }

    if n_tokens is None:
        token_addresses = []
        t = 0
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
    *,
    metadata: curve_spec.CurvePoolMetadata | None = None,
    n_tokens: int | None = None,
    provider: spec.ProviderReference = None,
) -> int:

    if isinstance(token, int):
        # token already an index
        return token

    elif isinstance(token, str) and token.startswith('0x'):
        # token an address
        if metadata is not None:
            pool_addresses = metadata['token_addresses']
        elif pool is not None:
            pool_addresses = await async_get_pool_tokens(
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
            pool_addresses = await async_get_pool_tokens(
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
    *,
    n_tokens: int | None = None,
    provider: spec.ProviderReference = None,
) -> curve_spec.CurvePoolMetadata:

    import asyncio

    function_abi: spec.FunctionABI = {
        'inputs': [],
        'name': 'A',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    }

    a_coroutine = rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        function_parameters=[],
        provider=provider,
    )
    a_task = asyncio.create_task(a_coroutine)

    # get addresses
    token_addresses = await async_get_pool_tokens(
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
