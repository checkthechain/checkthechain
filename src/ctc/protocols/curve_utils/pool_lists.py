from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

from ctc import evm
from ctc import rpc
from ctc import spec

from . import pool_metadata

old_pool_factory = '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae'
pool_factory = '0xb9fc157394af804a3578134a6585c0dc9cc990d4'
eth_address = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

creation_blocks = {
    '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae': 11942404,
    '0xb9fc157394af804a3578134a6585c0dc9cc990d4': 12903979,
}

function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'pool_count': {
        'inputs': [],
        'name': 'pool_count',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'pool_list': {
        'inputs': [{'name': 'arg0', 'type': 'uint256'}],
        'name': 'pool_list',
        'outputs': [{'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
}

event_abis = {
    'BasePoolAdded__old': {
        'anonymous': False,
        'inputs': [
            {'indexed': False, 'name': 'base_pool', 'type': 'address'},
            {'indexed': False, 'name': 'implementat', 'type': 'address'},
        ],
        'name': 'BasePoolAdded',
        'type': 'event',
    },
    'BasePoolAdded__new': {
        'anonymous': False,
        'inputs': [{'indexed': False, 'name': 'base_pool', 'type': 'address'}],
        'name': 'BasePoolAdded',
        'type': 'event',
    },
    'PlainPoolDeployed': {
        'anonymous': False,
        'inputs': [
            {'indexed': False, 'name': 'coins', 'type': 'address[4]'},
            {'indexed': False, 'name': 'A', 'type': 'uint256'},
            {'indexed': False, 'name': 'fee', 'type': 'uint256'},
            {'indexed': False, 'name': 'deployer', 'type': 'address'},
        ],
        'name': 'PlainPoolDeployed',
        'type': 'event',
    },
    'MetaPoolDeployed': {
        'anonymous': False,
        'inputs': [
            {'indexed': False, 'name': 'coin', 'type': 'address'},
            {'indexed': False, 'name': 'base_pool', 'type': 'address'},
            {'indexed': False, 'name': 'A', 'type': 'uint256'},
            {'indexed': False, 'name': 'fee', 'type': 'uint256'},
            {'indexed': False, 'name': 'deployer', 'type': 'address'},
        ],
        'name': 'MetaPoolDeployed',
        'type': 'event',
    },
}

#
# # call based
#


async def async_get_factory_pool_data(
    factory: spec.Address,
    include_balances: bool = False,
) -> list[CurvePoolData]:
    import asyncio

    n_pools = await rpc.async_eth_call(
        to_address=factory,
        function_abi=function_abis['pool_count'],
    )

    coroutines = [
        _async_get_pool_data(p, factory, include_balances=include_balances)
        for p in range(n_pools)
    ]

    return await asyncio.gather(*coroutines)


class CurvePoolData(TypedDict):
    address: spec.Address
    tokens: typing.Sequence[spec.Address]
    symbols: typing.Sequence[str]
    balances: typing.Sequence[int | float | None]


async def _async_get_pool_data(
    p: int,
    factory: spec.Address,
    *,
    include_balances: bool = False,
) -> CurvePoolData:
    pool = await rpc.async_eth_call(
        to_address=factory,
        function_abi=function_abis['pool_list'],
        function_parameters=[p],
    )

    coins = await rpc.async_eth_call(
        to_address=factory,
        function_name='get_coins',  # cannot inline because different new / old
        function_parameters=[pool],
    )
    coins = [coin for coin in coins if coin not in [eth_address]]

    valid_coins = [
        coin
        for coin in coins
        if coin
        not in ['0x0000000000000000000000000000000000000000', eth_address]
    ]
    symbols = await evm.async_get_erc20s_symbols(
        valid_coins,
    )

    if eth_address in coins:
        index = coins.index(eth_address)
        symbols.insert(index, 'ETH')

    if include_balances:
        balances: typing.MutableSequence[
            int | float | None
        ] = await evm.async_get_erc20s_balance_of(  # type: ignore
            tokens=valid_coins,
            address=pool,
        )
        if eth_address in coins:
            eth_balance = await evm.async_get_eth_balance(pool)
            balances.insert(index, eth_balance)
    else:
        balances = [None for coin in coins]

    return {
        'address': pool,
        'tokens': coins,
        'symbols': symbols,
        'balances': balances,
    }


#
# # event based
#


async def async_get_base_pools(
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    factory: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:
    import asyncio
    import pandas as pd

    if start_block is None:
        start_block = 12903979

    if factory is None:
        factory = pool_factory
    if factory == pool_factory:
        factories = [old_pool_factory, pool_factory]
    else:
        factories = [factory]

    # gather data
    coroutines = []
    for factory in factories:
        if start_block is None:
            factory_start_block = creation_blocks[factory]
        else:
            factory_start_block = start_block
        coroutine = evm.async_get_events(
            contract_address=factory,
            event_name='BasePoolAdded',
            start_block=factory_start_block,
            end_block=end_block,
            provider=provider,
            verbose=verbose,
        )
        coroutines.append(coroutine)
    dfs = await asyncio.gather(*coroutines)
    events = typing.cast(spec.DataFrame, pd.concat(dfs))

    # format data
    events = events.sort_index()
    events = events[['contract_address', 'transaction_hash', 'arg__base_pool']]
    events = events.rename(
        columns={
            'contract_address': 'factory',
            'arg__base_pool': 'pool',
        }
    )

    return events


async def async_get_plain_pools(
    *,
    factory: spec.Address | None = None,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:

    if start_block is None:
        start_block = 12903979

    if factory is None:
        factory = pool_factory

    events = await evm.async_get_events(
        contract_address=factory,
        event_name='PlainPoolDeployed',
        start_block=start_block,
        end_block=end_block,
        provider=provider,
        verbose=verbose,
    )
    events = events[
        [
            'transaction_hash',
            'contract_address',
            'arg__coins',
            'arg__A',
            'arg__fee',
            'arg__deployer',
        ]
    ]
    events = events.rename(
        columns={
            'contract_address': 'factory',
            'arg__coins': 'coins',
            'arg__A': 'A',
            'arg__fee': 'fee',
            'arg__deployer': 'deployer',
        }
    )
    return events


async def async_get_meta_pools(
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    factory: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:
    import asyncio
    import pandas as pd

    if factory is None:
        factory = pool_factory
    if factory == pool_factory:
        factories = [old_pool_factory, pool_factory]
    else:
        factories = [factory]

    # gather data
    coroutines = []
    for factory in factories:
        if start_block is None:
            factory_start_block: spec.BlockNumberReference = creation_blocks[
                factory
            ]
        else:
            factory_start_block = start_block
        coroutine = evm.async_get_events(
            contract_address=factory,
            event_name='MetaPoolDeployed',
            start_block=factory_start_block,
            end_block=end_block,
            provider=provider,
            verbose=verbose,
        )
        coroutines.append(coroutine)
    dfs = await asyncio.gather(*coroutines)
    events = typing.cast(spec.DataFrame, pd.concat(dfs))

    # format data
    events = events.sort_index()
    events = events[
        [
            'transaction_hash',
            'contract_address',
            'arg__coin',
            'arg__base_pool',
            'arg__A',
            'arg__fee',
            'arg__deployer',
        ]
    ]
    events = events.rename(
        columns={
            'contract_address': 'factory',
            'arg__coin': 'coin',
            'arg__base_pool': 'base_pool',
            'arg__A': 'A',
            'arg__fee': 'fee',
            'arg__deployer': 'deployer',
        }
    )

    return events


#
# # common dex_pool interface
#


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

    from ctc import db

    if factory is None:
        network, provider = evm.get_network_and_provider(network, provider)
        if network not in (1, 'mainnet'):
            raise Exception(
                'curve factory unknown for network: ' + str(network)
            )
        factory = pool_factory

    return await db.async_get_dex_pools(
        factory=factory,
        async_get_new_pools_of_factory=_async_get_new_pools,
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        update=update,
        network=network,
        provider=provider,
    )


async def _async_get_new_pools(
    *,
    factory: spec.Address,
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
) -> typing.Sequence[spec.DexPool]:

    start_block, end_block = await evm.async_block_numbers_to_int(
        [start_block, end_block]
    )

    start_pool_count, end_pool_count = await rpc.async_batch_eth_call(
        to_address=factory,
        function_abi=function_abis['pool_count'],
        block_numbers=[start_block, end_block],
    )

    pools = await rpc.async_batch_eth_call(
        to_address=factory,
        function_abi=function_abis['pool_list'],
        function_parameter_list=[
            [index] for index in range(start_pool_count, end_pool_count)
        ],
    )

    creation_blocks_coroutine = asyncio.create_task(
        evm.async_get_contracts_creation_blocks(pools)
    )

    coroutines = [pool_metadata.async_get_pool_tokens(pool) for pool in pools]
    pools_tokens = await asyncio.gather(*coroutines)

    creation_blocks = await creation_blocks_coroutine

    dex_pools = []
    for pool, pool_tokens, creation_block in zip(
        pools, pools_tokens, creation_blocks
    ):

        if len(pool_tokens) < 4:
            pool_tokens = pool_tokens + [None] * (4 - len(pool_tokens))
        if creation_block is None:
            raise Exception('could not determine creation block of pool')

        asset0 = pool_tokens[0]
        asset1 = pool_tokens[1]
        asset2 = pool_tokens[2]
        asset3 = pool_tokens[3]

        dex_pool: spec.DexPool = {
            'address': pool,
            'factory': factory,
            'asset0': asset0,
            'asset1': asset1,
            'asset2': asset2,
            'asset3': asset3,
            'fee': None,
            'creation_block': creation_block,
            'additional_data': {},
        }
        dex_pools.append(dex_pool)

    return dex_pools
