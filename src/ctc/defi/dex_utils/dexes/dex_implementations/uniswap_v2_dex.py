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
        context: spec.Context = None,
    ) -> typing.Sequence[spec.DexPool]:
        df = await evm.async_get_events(
            factory,
            event_abi=uniswap_v2_utils.factory_event_abis['PairCreated'],
            verbose=False,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            context=context,
        )

        dex_pools = []
        for row in df.to_dicts():
            dex_pool: spec.DexPool = {
                'address': row['arg__pair'],
                'factory': factory,
                'asset0': row['arg__token0'],
                'asset1': row['arg__token1'],
                'asset2': None,
                'asset3': None,
                'fee': int(0.003 * 1e8),
                'creation_block': row['block_number'],
                'additional_data': {},
            }
            dex_pools.append(dex_pool)
        return dex_pools

    @classmethod
    async def _async_get_pool_assets_from_node(
        cls,
        pool: spec.Address,
        *,
        block: spec.BlockNumberReference | None = None,
        context: spec.Context = None,
    ) -> tuple[str, str]:
        import asyncio
        from ctc.protocols import uniswap_v2_utils

        token0 = rpc.async_eth_call(
            function_abi=uniswap_v2_utils.pool_function_abis['token0'],
            to_address=pool,
            block_number=block,
            context=context,
        )
        token1 = rpc.async_eth_call(
            function_abi=uniswap_v2_utils.pool_function_abis['token1'],
            to_address=pool,
            block_number=block,
            context=context,
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
        context: spec.Context = None,
        verbose: bool = False,
    ) -> spec.RawDexTrades:
        import polars as pl

        trades = await evm.async_get_events(
            event_abi=uniswap_v2_utils.pool_event_abis['Swap'],
            contract_address=pool,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            include_timestamps=include_timestamps,
            verbose=verbose,
            context=context,
            integer_output_format=float,
        )

        df = trades.select(
            (pl.when(pl.col('arg__amount0Out') > 0).then(1).otherwise(0)).alias(
                'sold_id'
            ),
            (pl.col('arg__amount0In') + pl.col('arg__amount1In')).alias(
                'sold_amount'
            ),
            (pl.col('arg__amount0Out') + pl.col('arg__amount1Out')).alias(
                'bought_amount'
            ),
        )
        df = df.with_columns((1 - pl.col('sold_id')).alias('bought_id'))

        output: spec.RawDexTrades = {
            'block_number': trades['block_number'],
            'transaction_hash': trades['transaction_hash'],
            'recipient': trades['arg__to'],
            'sold_id': df['sold_id'],
            'bought_id': df['bought_id'],
            'sold_amount': df['sold_amount'],
            'bought_amount': df['bought_amount'],
        }

        if include_timestamps:
            output['timestamp'] = trades['timestamp']

        return output

