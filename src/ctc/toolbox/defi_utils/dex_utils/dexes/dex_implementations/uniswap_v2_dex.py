from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.protocols import uniswap_v2_utils
from .. import dex_class


class UniswapV2DEX(dex_class.DEX):
    """Uniswap V2 DEX"""

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
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Sequence[spec.DexPool]:

        network, provider = evm.get_network_and_provider(network, provider)

        df = await evm.async_get_events(
            factory,
            event_abi=uniswap_v2_utils.factory_event_abis['PairCreated'],
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

    @classmethod
    async def _async_get_pool_assets_from_node(
        cls,
        pool: spec.Address,
        *,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        block: spec.BlockNumberReference | None = None,
    ) -> tuple[str, str]:

        import asyncio
        from ctc.protocols import uniswap_v2_utils

        network, provider = evm.get_network_and_provider(network, provider)

        token0 = rpc.async_eth_call(
            function_abi=uniswap_v2_utils.pool_function_abis['token0'],
            to_address=pool,
            provider=provider,
            block_number=block,
        )
        token1 = rpc.async_eth_call(
            function_abi=uniswap_v2_utils.pool_function_abis['token1'],
            to_address=pool,
            provider=provider,
            block_number=block,
        )

        return await asyncio.gather(token0, token1)

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

        network, provider = evm.get_network_and_provider(network, provider)

        trades = await evm.async_get_events(
            event_abi=uniswap_v2_utils.pool_event_abis['Swap'],
            contract_address=pool,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            include_timestamps=include_timestamps,
            provider=provider,
            verbose=verbose,
            keep_multiindex=False,
        )

        sold_id = (trades['arg__amount0Out'].map(int) > 0).astype(int)
        bought_id = (sold_id == 0).astype(int)
        sold_amount = trades['arg__amount0In'].map(int) + trades[
            'arg__amount1In'
        ].map(int)
        bought_amount = trades['arg__amount0Out'].map(int) + trades[
            'arg__amount1Out'
        ].map(int)

        output: spec.RawDexTrades = {
            'transaction_hash': trades['transaction_hash'],
            'recipient': trades['arg__to'],
            'sold_id': sold_id,
            'bought_id': bought_id,
            'sold_amount': sold_amount,
            'bought_amount': bought_amount,
        }

        if include_timestamps:
            output['timestamp'] = trades['timestamp']

        return output
