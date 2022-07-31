from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ctc.toolbox.defi_utils import dex_utils
from . import uniswap_v3_spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_pools(
    factory: spec.Address | None = None,
    *,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    update: bool = False,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
) -> typing.Sequence[spec.DexPool]:

    if factory is None:
        # uniswap factory the same across all networks
        factory = uniswap_v3_spec.factory

    return await dex_utils.async_get_dex_pools(
        factory=factory,
        async_get_new_pools_of_factory=async_get_new_pools,
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        update=update,
        network=network,
        provider=provider,
    )


async def async_get_new_pools(
    *,
    factory: spec.Address,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
) -> typing.Sequence[spec.DexPool]:

    event_abi: spec.EventABI = {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'token0',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'token1',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'uint24',
                'name': 'fee',
                'type': 'uint24',
            },
            {
                'indexed': False,
                'internalType': 'int24',
                'name': 'tickSpacing',
                'type': 'int24',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'pool',
                'type': 'address',
            },
        ],
        'name': 'PoolCreated',
        'type': 'event',
    }

    start_block, end_block = await evm.async_parse_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=False,
    )

    df = await evm.async_get_events(
        factory,
        event_abi=event_abi,
        verbose=False,
        start_block=start_block,
        end_block=end_block,
        keep_multiindex=False,
    )

    dex_pools = []
    for index, row in df.iterrows():
        block = typing.cast(int, index)
        dex_pool: spec.DexPool = {
            'address': row['arg__pool'],
            'factory': factory,
            'asset0': row['arg__token0'],
            'asset1': row['arg__token1'],
            'asset2': None,
            'asset3': None,
            'fee': row['arg__fee'] * 100,
            'creation_block': block,
            'additional_data': {},
        }
        dex_pools.append(dex_pool)
    return dex_pools
