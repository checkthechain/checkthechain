from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ctc.toolbox.defi_utils import dex_utils
from . import uniswap_v2_spec


async def async_get_pools(
    factory: spec.Address | None = None,
    *,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    update: bool = False,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
) -> typing.Sequence[spec.DexPool]:

    if factory is None:
        network, provider = evm.get_network_and_provider(network, provider)
        if network not in (1, 'mainnet'):
            raise Exception(
                'uniswap v2 factory unknown for network: ' + str(network)
            )
        factory = uniswap_v2_spec.uniswap_v2_factory

    return await dex_utils.async_get_dex_pools(
        factory=factory,
        async_get_new_pools_of_factory=async_get_new_pools,
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        update=update,
        network=network,
        provider=provider,
    )


async def async_get_new_pools(
    *,
    factory: spec.Address,
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
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
                'indexed': False,
                'internalType': 'address',
                'name': 'pair',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'name': 'PairCreated',
        'type': 'event',
    }

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
            'address': row['arg__pair'],
            'factory': factory,
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
