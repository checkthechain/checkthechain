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
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Sequence[spec.DexPool]:

        network, provider = evm.get_network_and_provider(network, provider)

        balancer_pools = await evm.async_get_events(
            factory,
            event_abi=balancer_utils.vault_event_abis['PoolRegistered'],
            verbose=False,
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            keep_multiindex=False,
        )
        token_registrations = (
            await balancer_utils.async_get_token_registrations(
                factory=factory,
                start_block=start_block,
                end_block=end_block,
                provider=provider,
            )
        )

        dex_pools = []
        for index, row in balancer_pools.iterrows():

            block = typing.cast(int, index)

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
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        block: spec.BlockNumberReference | None = None,
    ) -> typing.Sequence[spec.Address]:

        network, provider = evm.get_network_and_provider(network, provider)

        result = await balancer_utils.async_get_pool_balances(
            pool_address=pool, provider=provider, block=block
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
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        verbose: bool = False,
    ) -> spec.RawDexTrades:

        network, provider = evm.get_network_and_provider(network, provider)

        network = evm.get_network_chain_id(network)
        vault = cls._pool_factories[network][0]
        if start_block is None:
            start_block = await evm.async_get_contract_creation_block(
                pool,
                provider=provider,
            )

        trades = await evm.async_get_events(
            vault,
            event_abi=balancer_utils.vault_event_abis['Swap'],
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            verbose=verbose,
            keep_multiindex=False,
        )

        assets = await cls.async_get_pool_assets(pool)

        # filter by pool
        pool_id = await balancer_utils.async_get_pool_id(
            pool_address=pool, provider=provider
        )
        mask = trades['arg__poolId'] == pool_id
        trades = trades[mask]

        import pandas as pd

        output: spec.RawDexTrades = {
            'transaction_hash': trades['transaction_hash'],
            'recipient': None,
            'sold_id': pd.Series(
                [
                    assets.index(address)
                    for address in trades['arg__tokenIn'].values
                ],
                index=trades.index,
            ),
            'bought_id': pd.Series(
                [
                    assets.index(address)
                    for address in trades['arg__tokenOut'].values
                ],
                index=trades.index,
            ),
            'sold_amount': trades['arg__amountIn'].map(int),
            'bought_amount': trades['arg__amountOut'].map(int),
        }

        if include_timestamps:
            output['timestamp'] = await evm.async_get_block_timestamps(
                blocks=trades.index.values,
                provider=provider,
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
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> int | float:

        from ctc.protocols import balancer_utils

        network, provider = evm.get_network_and_provider(network, provider)

        pool_balances = await balancer_utils.async_get_pool_balances(
            pool_address=pool,
            block=block,
            normalize=normalize,
            provider=provider,
        )
        return pool_balances[asset]
