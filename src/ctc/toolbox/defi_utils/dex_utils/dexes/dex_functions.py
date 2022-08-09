"""function wrappers of DEX methods"""

from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from .. import dexes
from . import dex_class
from . import dex_class_utils
from . import dex_directory

if typing.TYPE_CHECKING:
    import tooltime


# TODO: implement as a decorator that discovers DEX and uses it
# TODO: break into multiple files

#
# # pool lists
#


async def async_get_pools(
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    network: spec.NetworkReference | None = None,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    update: bool = False,
    provider: spec.ProviderReference | None = None,
) -> typing.Sequence[spec.DexPool]:

    # get dex
    all_dex_factories = dex is not None and factory is None
    if factory is None and dex is None:
        dex = dex_class.DEX
    else:
        dex = dex_class_utils.get_dex(
            dex=dex,
            factory=factory,
            network=network,
        )

    return await dex.async_get_pools(
        factory=factory,
        all_dex_factories=all_dex_factories,
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        update=update,
        provider=provider,
    )

#
# # pool metadata
#


async def async_get_pool_assets(
    pool: spec.Address,
    network: spec.NetworkReference | None = None,
    *,
    provider: spec.ProviderReference | None = None,
    use_db: bool = True,
    factory: spec.Address | None = None,
) -> typing.Sequence[spec.Address]:

    network, provider = evm.get_network_and_provider(network, provider)

    # try obtaining pool from db
    if use_db:
        from ctc import db

        pool_data = await db.async_query_dex_pool(address=pool, network=network)
        if pool_data is not None:
            assets: typing.MutableSequence[spec.Address] = []
            asset0 = pool_data['asset0']
            if asset0 is not None:
                assets.append(asset0)
            asset1 = pool_data['asset1']
            if asset1 is not None:
                assets.append(asset1)
            asset2 = pool_data['asset2']
            if asset2 is not None:
                assets.append(asset2)
            asset3 = pool_data['asset3']
            if asset3 is not None:
                assets.append(asset3)
            return assets

    # if not in db, acquire using RPC
    if factory is None:
        raise Exception('must specify factory if pool not in db')
    dex_name = dex_directory.get_dex_name_of_factory(
        factory=factory,
        network=network,
    )
    dex = dexes.get_dex(dex_name)
    return await dex.async_get_pool_assets(pool=pool, provider=provider)


#
# # pool state
#


async def async_get_pool_balance(
    pool: spec.Address,
    token: spec.Address,
    *,
    dex: typing.Type[dexes.DEX] | str | None = None,
    factory: spec.Address | None = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> int | float:
    """get balance of particular asset in pool"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dexes.get_dex(dex=dex, factory=factory, network=network)
    return await dex.async_get_pool_balance(
        pool=pool,
        token=token,
        block=block,
        normalize=normalize,
        network=network,
        provider=provider,
    )


async def async_get_pool_balances(
    pool: spec.Address,
    *,
    dex: typing.Type[dexes.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    block: spec.BlockNumberReference | None = None,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Mapping[spec.Address, int | float]:
    """get balances of all assets in pool"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dexes.get_dex(dex=dex, factory=factory, network=network)
    return await dex.async_get_pool_balances(
        pool=pool,
        network=network,
        normalize=normalize,
        block=block,
        provider=provider,
    )


async def async_get_pool_balance_by_block(
    pool: spec.Address,
    token: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    dex: typing.Type[dexes.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[int | float]:
    """get balances of particular asset in pool at specific blocks"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dexes.get_dex(dex=dex, factory=factory, network=network)
    return await dex.async_get_pool_balance_by_block(
        pool=pool,
        token=token,
        blocks=blocks,
        normalize=normalize,
        network=network,
        provider=provider,
    )


async def async_get_pool_balances_by_block(
    pool: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    dex: typing.Type[dexes.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Mapping[str, typing.Sequence[int | float]]:
    """get balances of all assets in pool at specific blocks"""

    network, provider = evm.get_network_and_provider(network, provider)
    dex = dexes.get_dex(dex=dex, factory=factory, network=network)
    return await dex.async_get_pool_balances_by_block(
        pool=pool,
        blocks=blocks,
        normalize=normalize,
        network=network,
        provider=provider,
    )
