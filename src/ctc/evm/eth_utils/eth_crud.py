from __future__ import annotations

import asyncio
import typing

from ctc import rpc
from ctc import spec


async def async_get_eth_total_supply():
    import aiohttp

    url = 'http://api.etherscan.io/api?module=stats&action=ethsupply'
    session = aiohttp.ClientSession()
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception('could not get result')
        result = await response.json()
        return int(result['result'])


#
# # balances
#


@typing.overload
async def async_get_eth_balance(
    address: spec.Address,
    normalize: typing.Literal[False],
    provider: typing.Optional[spec.ProviderSpec] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> int:
    ...


@typing.overload
async def async_get_eth_balance(
    address: spec.Address,
    normalize: bool = True,
    provider: typing.Optional[spec.ProviderSpec] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> float:
    ...


async def async_get_eth_balance(
    address: spec.Address,
    normalize: bool = True,
    provider: typing.Optional[spec.ProviderSpec] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> typing.Union[int, float]:

    balance = await rpc.async_eth_get_balance(
        address=address,
        provider=provider,
        block_number=block,
    )

    if normalize:
        balance /= 1e18

    return balance


@typing.overload
async def async_get_eth_balance_by_block(
    address: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: typing.Literal[False],
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> list[int]:
    ...


@typing.overload
async def async_get_eth_balance_by_block(
    address: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: typing.Literal[True] = True,
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> list[float]:
    ...


async def async_get_eth_balance_by_block(
    address: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> typing.Union[list[int], list[float]]:

    coroutines = []
    for block in blocks:
        coroutine = async_get_eth_balance(
            address=address, provider=provider, block=block, normalize=normalize
        )
        coroutines.append(coroutine)

    return await asyncio.gather(*coroutines)


@typing.overload
async def async_get_eth_balance_of_addresses(
    addresses: spec.Address,
    block: typing.Sequence[spec.BlockNumberReference],
    normalize: typing.Literal[False],
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> list[int]:
    ...


@typing.overload
async def async_get_eth_balance_of_addresses(
    addresses: spec.Address,
    block: typing.Sequence[spec.BlockNumberReference],
    normalize: typing.Literal[True] = True,
    provider: typing.Optional[spec.ProviderSpec] = None,
) -> list[float]:
    ...


async def async_get_eth_balance_of_addresses(
    addresses: typing.Sequence[spec.Address],
    normalize: bool = True,
    provider: typing.Optional[spec.ProviderSpec] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> typing.Union[list[int], list[float]]:

    balances = await rpc.async_batch_eth_get_balance(
        addresses=addresses,
        provider=provider,
        block_number=block,
    )

    if normalize:
        balances = [balance / 1e18 for balance in balances]

    return balances

