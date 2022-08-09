from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ctc.protocols import balancer_utils
from .. import dex_class

if typing.TYPE_CHECKING:
    import tooltime


class BalancerDEX(dex_class.DEX):

    _pool_factories = {1: ['0xba12222222228d8ba445958a75a0704d566bf2c8']}

    @classmethod
    async def async_get_pool_assets(
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
    async def async_get_pool_balance(
        cls,
        pool: spec.Address,
        token: spec.Address,
        *,
        factory: spec.Address | None = None,
        normalize: bool = True,
        block: spec.BlockNumberReference | None = None,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> int | float:

        from ctc.protocols import balancer_utils

        pool_balances = await balancer_utils.async_get_pool_balances(
            pool_address=pool,
            block=block,
            normalize=normalize,
        )
        return pool_balances[token]

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
                    'internalType': 'bytes32',
                    'name': 'poolId',
                    'type': 'bytes32',
                },
                {
                    'indexed': True,
                    'internalType': 'address',
                    'name': 'poolAddress',
                    'type': 'address',
                },
                {
                    'indexed': False,
                    'internalType': 'enum IVault.PoolSpecialization',
                    'name': 'specialization',
                    'type': 'uint8',
                },
            ],
            'name': 'PoolRegistered',
            'type': 'event',
        }

        start_block, end_block = await evm.async_parse_block_range(
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            allow_none=False,
        )

        balancer_pools = await evm.async_get_events(
            factory,
            event_abi=event_abi,
            verbose=False,
            start_block=start_block,
            end_block=end_block,
            keep_multiindex=False,
        )
        token_registrations = await balancer_utils.async_get_token_registrations(
            factory=factory,
            start_block=start_block,
            end_block=end_block,
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
