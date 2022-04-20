from __future__ import annotations

import asyncio
import typing

from ctc import rpc
from ctc import spec

from .. import rari_abis
from . import directory_metadata
from . import token_metadata


async def async_get_pool_ctoken(
    comptroller: spec.Address,
    underlying: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    return await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_function_abis['cTokensByUnderlying'],
        function_parameters=[underlying],
    )


async def async_get_pool_ctokens(
    comptroller: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> tuple[spec.Address]:
    return await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_function_abis['getAllMarkets'],
    )


async def async_get_pool_underlying_tokens(
    *,
    ctokens: typing.Sequence[spec.Address] | None = None,
    comptroller: spec.Address | None = None,
    block: spec.BlockNumberReference = 'latest',
) -> dict[spec.Address, spec.Address]:
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
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    return await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_function_abis['oracle'],
    )


async def async_get_pool_name(
    comptroller: spec.Address,
    all_pools: list[list[typing.Any]] | None = None,
    block: spec.BlockNumberReference = 'latest',
) -> str:
    comptroller = comptroller.lower()
    if all_pools is None:
        all_pools = await directory_metadata.async_get_all_pools(block=block)
    for pool in all_pools:
        if pool[2] == comptroller:
            return pool[0]
    else:
        raise Exception('could not find pool')

