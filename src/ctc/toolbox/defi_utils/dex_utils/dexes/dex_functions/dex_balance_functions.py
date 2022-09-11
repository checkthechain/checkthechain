from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from .. import dex_class
from .. import dex_class_utils


async def async_get_pool_balance(
    pool: spec.Address,
    asset: spec.Address,
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> int | float:
    """get balance of particular asset in pool"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, network=network
    )
    return await dex.async_get_pool_balance(
        pool=pool,
        asset=asset,
        block=block,
        normalize=normalize,
        network=network,
        provider=provider,
    )


async def async_get_pool_balances(
    pool: spec.Address,
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    block: spec.BlockNumberReference | None = None,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Mapping[spec.Address, int | float]:
    """get balances of all assets in pool"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, network=network
    )
    return await dex.async_get_pool_balances(
        pool=pool,
        network=network,
        normalize=normalize,
        block=block,
        provider=provider,
    )


async def async_get_pool_balance_by_block(
    pool: spec.Address,
    asset: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[int | float]:
    """get balances of particular asset in pool at specific blocks"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, network=network
    )
    return await dex.async_get_pool_balance_by_block(
        pool=pool,
        asset=asset,
        blocks=blocks,
        normalize=normalize,
        network=network,
        provider=provider,
    )


async def async_get_pool_balances_by_block(
    pool: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Mapping[str, typing.Sequence[int | float]]:
    """get balances of all assets in pool at specific blocks"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, network=network
    )
    return await dex.async_get_pool_balances_by_block(
        pool=pool,
        blocks=blocks,
        normalize=normalize,
        network=network,
        provider=provider,
    )
