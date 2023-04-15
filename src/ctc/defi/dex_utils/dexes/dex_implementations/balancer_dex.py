from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ctc.protocols import balancer_utils
from .. import dex_class

if typing.TYPE_CHECKING:
    import tooltime


class BalancerDEX(dex_class.DEX):
    """Balancer DEX"""

    _pool_factories = {1: ['0xba12222222228d8ba445958a75a0704d566bf2c8']}

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

        balancer_pools = await evm.async_get_events(
            factory,
            event_abi=balancer_utils.vault_event_abis['PoolRegistered'],
            verbose=False,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            context=context,
        )
        token_registrations = (
            await balancer_utils.async_get_token_registrations(
                factory=factory,
                start_block=start_block,
                end_block=end_block,
                context=context,
            )
        )

        dex_pools = []
        for row in balancer_pools.iter_rows(named=True):

            block = int(row['block_number'])

            assets: typing.Sequence[str | None] = token_registrations.get(
                row['arg__poolId'], []
            )
            if len(assets) < 4:
                assets = list(assets) + [None] * (4 - len(assets))
            if len(assets) > 4:
                additional_data = {'additional_assets': assets[4:]}
                assets = assets[:4]
            else:
                additional_data = {}
            asset0 = assets[0]
            asset1 = assets[1]
            asset2 = assets[2]
            asset3 = assets[3]

            dex_pool: spec.DexPool = {
                'address': row['arg__poolAddress'],
                'factory': factory,
                'asset0': asset0,
                'asset1': asset1,
                'asset2': asset2,
                'asset3': asset3,
                'creation_block': block,
                'fee': None,
                'additional_data': additional_data,
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
    ) -> typing.Sequence[spec.Address]:

        result = await balancer_utils.async_get_pool_balances(
            pool_address=pool, context=context, block=block
        )

        return list(result.keys())

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
        verbose: bool = False,
        context: spec.Context = None,
    ) -> spec.RawDexTrades:

        from ctc import config

        network = config.get_context_chain_id(context)
        vault = cls._pool_factories[network][0]
        if start_block is None:
            start_block = await evm.async_get_contract_creation_block(
                pool,
                context=context,
            )

        trades = await evm.async_get_events(
            vault,
            event_abi=balancer_utils.vault_event_abis['Swap'],
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            verbose=verbose,
        )

        assets = await cls.async_get_pool_assets(pool)

        # filter by pool
        pool_id = await balancer_utils.async_get_pool_id(
            pool_address=pool, context=context
        )
        mask = trades['arg__poolId'] == pool_id
        trades = trades[mask]

        import polars as pl

        output: spec.RawDexTrades = {
            'block_number': trades['block_number'],
            'transaction_hash': trades['transaction_hash'],
            'recipient': None,
            'sold_id': pl.Series(
                [
                    assets.index(address)
                    for address in trades['arg__tokenIn'].to_list()
                ],
            ),
            'bought_id': pl.Series(
                [
                    assets.index(address)
                    for address in trades['arg__tokenOut'].to_list()
                ],
            ),
            'sold_amount': trades['arg__amountIn'].apply(int),
            'bought_amount': trades['arg__amountOut'].apply(int),
        }

        if include_timestamps:
            output['timestamp'] = await evm.async_get_block_timestamps(
                blocks=trades['block_number'].to_list(),
                context=context,
            )

        return output

    @classmethod
    async def async_get_pool_balance(
        cls,
        pool: spec.Address,
        asset: spec.Address,
        *,
        factory: spec.Address | None = None,
        normalize: bool = True,
        block: spec.BlockNumberReference | None = None,
        context: spec.Context = None,
    ) -> int | float:

        from ctc.protocols import balancer_utils

        pool_balances = await balancer_utils.async_get_pool_balances(
            pool_address=pool,
            block=block,
            normalize=normalize,
            context=context,
        )
        return pool_balances[asset]

