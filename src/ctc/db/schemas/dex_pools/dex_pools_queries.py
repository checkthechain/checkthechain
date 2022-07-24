from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from .. import query_utils
from . import dex_pools_statements
from . import dex_pools_intake


async_query_dex_pool = query_utils.wrap_selector_with_connection(
    dex_pools_statements.async_select_dex_pool,
    'dex_pools',
)


async_query_dex_pools = query_utils.wrap_selector_with_connection(
    dex_pools_statements.async_select_dex_pools,
    'dex_pools',
)

async_query_dex_pool_factory_last_scanned_block = (
    query_utils.wrap_selector_with_connection(
        dex_pools_statements.async_select_dex_pool_factory_last_scanned_block,
        'dex_pools',
    )
)


async def async_get_pools(
    factory: spec.Address,
    async_get_new_pools_of_factory: typing.Callable[
        ...,
        typing.Coroutine[typing.Any, typing.Any, typing.Sequence[spec.DexPool]],
    ],
    *,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    update: bool = False,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
) -> typing.Sequence[spec.DexPool]:
    """return pools"""

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

    # get old pools
    pools: typing.MutableSequence[
        spec.DexPool
    ] | None = await async_query_dex_pools(  # type: ignore
        factory=factory,
        assets=assets,
        network=network,
        start_block=start_block,
        end_block=end_block,
    )
    if pools is None:
        pools = []

    if update:

        # get new pools
        last_scanned_block = (
            await async_query_dex_pool_factory_last_scanned_block(
                factory=factory,
                network=network,
            )
        )
        if last_scanned_block is None:
            last_scanned_block = None

        # faster to obtain from event cache or from db?
        latest_block = await evm.async_get_latest_block_number()
        new_pools = await async_get_new_pools_of_factory(
            factory=factory,
            start_block=last_scanned_block,
            end_block=latest_block,
        )
        await dex_pools_intake.async_intake_dex_pools(
            factory=factory,
            dex_pools=new_pools,
            network=network,
            last_scanned_block=latest_block,
        )

        # filter the new pools according to input arguments
        for new_pool in new_pools:

            # check asset filter
            include = True
            if assets is not None:
                keys = ['asset0', 'asset1', 'asset2', 'asset3']
                for asset in assets:
                    asset = asset.lower()
                    include = any(new_pool[key] == asset for key in keys)  # type: ignore
                    if not include:
                        break
            if not include:
                continue

            # check block range
            if start_block is not None and (
                new_pool['creation_block'] is None
                or new_pool['creation_block'] < start_block
            ):
                continue
            if end_block is not None and (
                new_pool['creation_block'] is None
                or new_pool['creation_block'] > end_block
            ):
                continue

            pools.append(new_pool)

    return pools
