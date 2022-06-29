from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from .. import rari_abis
from . import directory_metadata
from . import token_metadata


async def async_get_pool_ctoken(
    comptroller: spec.Address,
    underlying: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    result = await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_function_abis['cTokensByUnderlying'],
        function_parameters=[underlying],
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_ctokens(
    comptroller: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
) -> tuple[spec.Address]:
    result = await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_function_abis['getAllMarkets'],
    )
    if not isinstance(result, tuple) or not all(
        isinstance(item, str) for item in result
    ):
        raise Exception('invalid rpc result')
    return typing.cast(typing.Tuple[str], result)


async def async_get_pool_underlying_tokens(
    *,
    ctokens: typing.Sequence[spec.Address] | None = None,
    comptroller: spec.Address | None = None,
    block: spec.BlockNumberReference = 'latest',
) -> typing.Mapping[spec.Address, spec.Address]:
    import asyncio

    if ctokens is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        ctokens = await async_get_pool_ctokens(comptroller, block=block)

    coroutines = [
        token_metadata.async_get_ctoken_underlying(ctoken=ctoken)
        for ctoken in ctokens
    ]
    underlyings = await asyncio.gather(*coroutines)
    return dict(zip(ctokens, underlyings))


async def async_get_pool_oracle(
    comptroller: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    result = await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_function_abis['oracle'],
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_name(
    comptroller: spec.Address,
    *,
    all_pools: typing.Sequence[typing.Sequence[typing.Any]] | None = None,
    block: spec.BlockNumberReference = 'latest',
) -> str:
    comptroller = comptroller.lower()
    if all_pools is None:
        all_pools = await directory_metadata.async_get_all_pools(block=block)
    for pool in all_pools:
        if pool[2] == comptroller:
            output = pool[0]
            if not isinstance(output, str):
                raise Exception('invalid rpc result')
            return output
    else:
        raise Exception('could not find pool')
