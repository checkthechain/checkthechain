from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from .. import dex_class
from . import uniswap_v2_dex

if typing.TYPE_CHECKING:
    import tooltime


class UniswapV3DEX(dex_class.DEX):
    """Uniswap V3 DEX"""

    _pool_factories = {1: ['0x1f98431c8ad98523631ae4a59f267346ea31f984']}

    @classmethod
    async def async_get_new_pools(
        cls,
        *,
        factory: spec.Address,
        start_block: spec.BlockNumberReference | None = None,
        end_block: spec.BlockNumberReference | None = None,
        start_time: tooltime.Timestamp | None = None,
        end_time: tooltime.Timestamp | None = None,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Sequence[spec.DexPool]:

        from ctc.protocols import uniswap_v3_utils

        network, provider = evm.get_network_and_provider(network, provider)

        df = await evm.async_get_events(
            factory,
            event_abi=uniswap_v3_utils.factory_event_abis['PoolCreated'],
            verbose=False,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            keep_multiindex=False,
            provider=provider,
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

    @classmethod
    async def _async_get_pool_assets_from_node(
        cls,
        pool: spec.Address,
        *,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        block: spec.BlockNumberReference | None = None,
    ) -> tuple[str, str]:
        output = uniswap_v2_dex.UniswapV2DEX._async_get_pool_assets_from_node(
            pool=pool,
            network=network,
            provider=provider,
            block=block,
        )
        return await output

    @classmethod
    async def _async_get_pool_raw_trades(
        cls,
        pool: spec.Address,
        *,
        start_block: spec.BlockNumberReference | None = None,
        end_block: spec.BlockNumberReference | None = None,
        start_time: tooltime.Timestamp | None = None,
        end_time: tooltime.Timestamp | None = None,
        include_timestamps: bool = False,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        verbose: bool = False,
    ) -> spec.RawDexTrades:

        from ctc.protocols import uniswap_v3_utils

        network, provider = evm.get_network_and_provider(network, provider)

        event_abi = await uniswap_v3_utils.async_get_event_abi('Swap', 'pool')

        trades = await evm.async_get_events(
            event_abi=event_abi,
            contract_address=pool,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            include_timestamps=include_timestamps,
            verbose=verbose,
            keep_multiindex=False,
        )

        bool_bought_id = trades['arg__amount0'].map(int) > 0
        bought_id = bool_bought_id.map(int)
        sold_id = (bought_id == 0).map(int)
        sold_amount = sold_id * trades['arg__amount1'].map(
            int
        ) + bought_id * trades['arg__amount0'].map(int)
        bought_amount = -(
            bought_id * trades['arg__amount1'].map(int)
            + sold_id * trades['arg__amount0'].map(int)
        )

        output: spec.RawDexTrades = {
            'transaction_hash': trades['transaction_hash'],
            'recipient': trades['arg__recipient'],
            'sold_id': sold_id,
            'bought_id': bought_id,
            'sold_amount': sold_amount,
            'bought_amount': bought_amount,
        }

        return output
