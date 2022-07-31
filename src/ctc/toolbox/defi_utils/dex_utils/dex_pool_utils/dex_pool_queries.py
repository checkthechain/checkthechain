from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec


if typing.TYPE_CHECKING:
    NewPoolGetter = typing.Callable[
        ...,
        typing.Coroutine[
            typing.Any,
            typing.Any,
            typing.Sequence[spec.DexPool],
        ],
    ]


def get_dex_pool_factory_platforms(
    network: spec.NetworkReference,
) -> typing.Mapping[spec.Address, str]:

    if network in (1, 'mainnet'):
        return {
            '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f': 'Uniswap V2',
            '0x1f98431c8ad98523631ae4a59f267346ea31f984': 'Uniswap V3',
            '0xba12222222228d8ba445958a75a0704d566bf2c8': 'Balancer',
            '0xb9fc157394af804a3578134a6585c0dc9cc990d4': 'Curve',
            '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae': 'Curve',
            '0xf18056bbd320e96a48e3fbf8bc061322531aac99': 'Curve',
            '0x90e00ace148ca3b23ac1bc8c240c2a7dd9c2d7f5': 'Curve',
            '0x8f942c20d02befc377d41445793068908e2250d0': 'Curve',
            '0xbabe61887f1de2713c6f97e567623453d3c79f67': 'Curve',
            '0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac': 'Sushi',
        }
    else:
        raise Exception(
            'dex pool factory map not available for network: ' + str(network)
        )


def get_new_pool_getter(
    factory: spec.Address,
    network: spec.NetworkReference,
) -> NewPoolGetter:

    # get platform
    platforms = get_dex_pool_factory_platforms(network=network)
    if factory not in platforms:
        raise Exception('unknown dex pool factory: ' + str(factory))
    platform = platforms[factory]

    # get getter
    if platform == 'Uniswap V2':
        from ctc.protocols import uniswap_v2_utils

        return uniswap_v2_utils.async_get_new_pools
    elif platform == 'Uniswap V3':
        from ctc.protocols import uniswap_v3_utils

        return uniswap_v3_utils.async_get_new_pools
    elif platform == 'Balancer':
        from ctc.protocols import balancer_utils

        return balancer_utils.async_get_new_pools
    elif platform == 'Curve':
        from ctc.protocols import curve_utils

        return curve_utils.async_get_new_pools
    elif platform == 'Sushi':
        from ctc.protocols import uniswap_v2_utils

        return uniswap_v2_utils.async_get_new_pools
    else:
        raise Exception('unknown dex platform ' + str(platform))


async def async_get_dex_pools(
    *,
    factory: spec.Address | None = None,
    factories: typing.Sequence[spec.Address] | None = None,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    update: bool = False,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
    async_get_new_pools_of_factory: NewPoolGetter | None = None,
) -> typing.Sequence[spec.DexPool]:
    """return pools"""

    if assets is not None and len(assets) == 0:
        assets = None

    if factory is None:
        # TODO: do this using native sql queries instead of in python
        if factories is not None:
            coroutines = [
                async_get_dex_pools(
                    factory=factory,
                    assets=assets,
                    start_block=start_block,
                    end_block=end_block,
                    update=update,
                    network=network,
                    provider=provider,
                )
                for factory in factories
            ]
            results = await asyncio.gather(*coroutines)
            return [subresult for result in results for subresult in result]

    network, provider = evm.get_network_and_provider(network, provider)

    if start_block is not None:
        start_block = await evm.async_block_number_to_int(
            start_block,
            provider=provider,
        )
    if end_block is not None:
        end_block = await evm.async_block_number_to_int(
            end_block,
            provider=provider,
        )

    pools = await _async_get_known_dex_pools(
        factory=factory,
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        network=network,
    )

    if update:

        new_pools = await async_update_latest_dex_pools(
            factory=factory,
            network=network,
            provider=provider,
            async_get_new_pools_of_factory=async_get_new_pools_of_factory,
        )

        new_pools = _filter_pools(
            pools=new_pools,
            assets=assets,
            start_block=start_block,
            end_block=end_block,
        )

        pools = list(pools) + list(new_pools)

    return pools


async def _async_get_known_dex_pools(
    *,
    factory: spec.Address | None = None,
    network: spec.NetworkReference,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[spec.DexPool]:
    """return pools"""

    from ctc import db

    pools = await db.async_query_dex_pools(
        factory=factory,
        assets=assets,
        network=network,
        start_block=start_block,
        end_block=end_block,
    )
    if pools is None:
        pools = []

    return pools


#
# # update pools
#


async def async_update_latest_dex_pools(
    *,
    factory: spec.Address | None = None,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    async_get_new_pools_of_factory: NewPoolGetter | None = None,
) -> typing.Sequence[spec.DexPool]:

    network, provider = evm.get_network_and_provider(network, provider)

    if factory is not None:
        return await async_update_latest_dex_pools_of_factory(
            factory=factory,
            network=network,
            provider=provider,
            async_get_new_pools_of_factory=async_get_new_pools_of_factory,
        )
    else:

        # update all factories

        platforms = get_dex_pool_factory_platforms(network=network)

        coroutines = []
        for factory in platforms.keys():
            coroutine = async_update_latest_dex_pools_of_factory(
                factory=factory,
                network=network,
                provider=provider,
            )
            coroutines.append(coroutine)
        results = await asyncio.gather(*coroutines)

        return [dex_pool for result in results for dex_pool in result]


async def async_update_latest_dex_pools_of_factory(
    factory: spec.Address,
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    async_get_new_pools_of_factory: NewPoolGetter | None = None,
) -> typing.Sequence[spec.DexPool]:

    from ctc import db

    network, provider = evm.get_network_and_provider(network, provider)

    # get new pools
    last_scanned_block = (
        await db.async_query_dex_pool_factory_last_scanned_block(
            factory=factory,
            network=network,
        )
    )
    if last_scanned_block is None:
        from ctc.toolbox import search_utils

        try:
            creation_block = await evm.async_get_contract_creation_block(factory)
            if creation_block is None:
                raise Exception('could not determine factory creation block')
            last_scanned_block = creation_block - 1
        except search_utils.NoMatchFound:
            last_scanned_block = -1

    latest_block = await evm.async_get_latest_block_number()

    if last_scanned_block + 1 <= latest_block:

        if async_get_new_pools_of_factory is None:
            async_get_new_pools_of_factory = get_new_pool_getter(
                factory=factory,
                network=network,
            )

        new_pools = await async_get_new_pools_of_factory(
            factory=factory,
            start_block=last_scanned_block + 1,
            end_block=latest_block,
        )
        await db.async_intake_dex_pools(
            factory=factory,
            dex_pools=new_pools,
            network=network,
            last_scanned_block=latest_block,
        )

    else:
        new_pools = []

    return new_pools


#
# # pool filters
#


def _filter_pools(
    *,
    pools: typing.Sequence[spec.DexPool],
    assets: typing.Sequence[str] | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
) -> typing.Sequence[spec.DexPool]:

    filtered = []

    # filter the new pools according to input arguments
    for pool in pools:

        # check asset filter
        include = True
        if assets is not None:
            keys = ['asset0', 'asset1', 'asset2', 'asset3']
            for asset in assets:
                asset = asset.lower()
                include = any(pool[key] == asset for key in keys)  # type: ignore
                if not include:
                    break
        if not include:
            continue

        # check block range
        if start_block is not None and (
            pool['creation_block'] is None
            or pool['creation_block'] < start_block
        ):
            continue
        if end_block is not None and (
            pool['creation_block'] is None or pool['creation_block'] > end_block
        ):
            continue

        filtered.append(pool)

    return filtered
