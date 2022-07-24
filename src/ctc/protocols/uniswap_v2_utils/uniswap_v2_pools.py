from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from . import uniswap_v2_spec


async def async_get_pools(
    *,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    factory: spec.Address | None = None,
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

    from ctc import db

    if factory is None:
        factory = uniswap_v2_spec.uniswap_v2_factory

    # get old pools
    pools: typing.MutableSequence[
        spec.DexPool
    ] | None = await db.async_query_dex_pools(  # type: ignore
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
            await db.async_query_dex_pool_factory_last_scanned_block(
                factory=factory,
                network=network,
            )
        )
        if last_scanned_block is None:
            last_scanned_block = None

        # faster to obtain from event cache or from db?
        latest_block = await evm.async_get_latest_block_number()
        new_pools_df = await evm.async_get_events(
            factory,
            event_name='PairCreated',
            verbose=False,
            start_block=last_scanned_block,
            end_block=latest_block,
            keep_multiindex=False,
        )
        new_pools = _uniswap_v2_events_to_dex_pools(new_pools_df)
        await db.async_intake_dex_pools(
            new_pools, network=network, last_scanned_block=latest_block
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


def _uniswap_v2_events_to_dex_pools(
    df: spec.DataFrame,
) -> typing.MutableSequence[spec.DexPool]:
    dex_pools = []
    for index, row in df.iterrows():
        block = typing.cast(int, index)
        dex_pool: spec.DexPool = {
            'address': row['arg__pair'],
            'factory': row['address'],
            'asset0': row['arg__token0'],
            'asset1': row['arg__token1'],
            'asset2': None,
            'asset3': None,
            'fee': int(0.003 * 1e8),
            'creation_block': block,
            'additional_data': {},
        }
        dex_pools.append(dex_pool)
    return dex_pools
