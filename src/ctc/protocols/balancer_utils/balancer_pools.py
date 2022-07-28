from __future__ import annotations

import ast
import typing

from ctc import evm
from ctc import spec
from ctc.toolbox.defi_utils import dex_utils
from . import balancer_spec


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
                'balancer vault unknown for network: ' + str(network)
            )

        factory = balancer_spec.vault

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

    balancer_pools = await evm.async_get_events(
        factory,
        event_abi=event_abi,
        verbose=False,
        start_block=start_block,
        end_block=end_block,
        keep_multiindex=False,
    )
    tokens_by_pool = await _async_get_tokens_by_pool(
        factory=factory,
        start_block=start_block,
        end_block=end_block,
    )

    dex_pools = []
    for index, row in balancer_pools.iterrows():

        block = typing.cast(int, index)

        assets: typing.Sequence[str | None] = tokens_by_pool.get(
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


async def _async_get_tokens_by_pool(
    factory: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
) -> typing.Mapping[str, typing.Sequence[str]]:

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
                'indexed': False,
                'internalType': 'contract IERC20[]',
                'name': 'tokens',
                'type': 'address[]',
            },
            {
                'indexed': False,
                'internalType': 'address[]',
                'name': 'assetManagers',
                'type': 'address[]',
            },
        ],
        'name': 'TokensRegistered',
        'type': 'event',
    }

    balancer_token_registrations = await evm.async_get_events(
        factory,
        event_abi=event_abi,
        verbose=False,
        start_block=start_block,
        end_block=end_block,
    )
    balancer_token_registrations['arg__tokens'] = balancer_token_registrations[
        'arg__tokens'
    ].map(ast.literal_eval)

    tokens_by_pool: typing.MutableMapping[str, typing.MutableSequence[str]] = {}
    for index, row in balancer_token_registrations.iterrows():
        pool = row['arg__poolId']

        tokens_by_pool.setdefault(pool, [])
        tokens_by_pool[pool].extend(row['arg__tokens'])

    return tokens_by_pool
