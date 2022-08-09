from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

from ctc import evm
from ctc import spec
from ctc.protocols import uniswap_v2_utils
from .. import dex_class


class UniswapV2DEX(dex_class.DEX):

    _pool_factories = {1: [uniswap_v2_utils.uniswap_v2_factory]}

    @classmethod
    async def async_get_new_pools(
        cls,
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
            start_time=None,
            end_time=None,
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
