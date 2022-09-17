from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

from ctc import evm
from ctc import rpc
from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


# factories
curve_deployer_eoa = '0xbabe61887f1de2713c6f97e567623453d3c79f67'
old_pool_factory = '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae'
pool_factory = '0xb9fc157394af804a3578134a6585c0dc9cc990d4'
deposit_separated_factory = '0xf18056bbd320e96a48e3fbf8bc061322531aac99'
crypto_factory = '0x8f942c20d02befc377d41445793068908e2250d0'
regular_factory = '0x90e00ace148ca3b23ac1bc8c240c2a7dd9c2d7f5'

eth_address = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

administrative_addresses = {
    'address_provider': '0x0000000022d53366457f9d5e68ec105046fc4383',
    'pool_registry': '0x90e00ace148ca3b23ac1bc8c240c2a7dd9c2d7f5',
    'registry_registry': '0x81c46feca27b31f3adc2b91ee4be9717d1cd3dd7',
}

creation_blocks = {
    '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae': 11942404,
    '0xb9fc157394af804a3578134a6585c0dc9cc990d4': 12903979,
}


# list from curve docs and manually going through non-factory pools on main page
def get_non_factory_pools() -> typing.Mapping[str, int]:
    return {
        '0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7': 10809473,  # 3Pool
        # '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490': 10809467,  # 3Pool
        # '0xfd2a8fa60abd58efe3eee34dd494cd491dc14900': 11497098,  # AAVE
        '0xdebf20617708857ebe4f679508e7b7863a8a8eee': 11497106,  # AAVE
        '0xa96a65c051bf88b4095ee1f2451c2a9d43f53ae2': 11774139,  # ankrETH
        # '0xaa17a236f2badc98ddc0cf999abb47d47fc0a6cf': 11774119,  # ankrETH
        '0x79a8c46dea5ada233abaffd40f3a0a2b1e5a4f27': 9567295,  # BUSD
        # '0xb6c057591e073249f2d9d88ba59a46cfc9b59edb': 9832521,  # BUSD
        # '0x3b3ac5386837dc563660fb6a0937dfaa5924333b': 9567293,  # BUSD
        '0xa2b47e3d5c44877cca798226b7b8118f9bfb7a56': 9554040,  # Compound
        # '0xeb21209ae4c2c9ff2a86aca31e123764a3b6bc06': 9832215,  # Compound
        # '0x845838df265dcd2c412a1dc9e959c7d08537f8a2': 9554031,  # Compound
        '0x0ce6a5ff5217e38315f87032cf90686c96627caa': 11466871,  # EURS
        # '0x194ebd173f6cdace046c53eacce9b953f28411d1': 11466859,  # EURS
        '0x4ca9b3063ec5866a4b82e437059d2c43d1be596f': 10732328,  # hBTC
        # '0xb19059ebb43466c323583928285a49f558e572fd': 10732326,  # hBTC
        '0x2dded6da1bf5dbdf597c45fcfaa3194e53ecfeaf': 11831119,  # IronBank
        # '0x5282a4ef67d9c33135340fb3289cc1711c13638c': 11831114,  # IronBank
        '0xf178c0b5bb7e7abf4e12a4838c7b7c5ba2c623c0': 11875215,  # Link
        # '0xcee60cfa923170e4f8204ae08b4fa6a3f5656f3a': 11875162,  # Link
        # '0xa50ccc70b6a011cffddf45057e39679379187287': 10041096,  # PAX
        '0x06364f10b501e868329afbc005b3492902d6c763': 10041041,  # PAX
        # '0xd905e2eaebe188fc92179b6350807d8bd91db0d8': 10041032,  # PAX
        '0x93054188d876f558f4a66b2ef1d97d16edf0895b': 10151385,  # renBTC
        # '0x49849c98ae39fff122806c06791fa73784fb3675': 10151366,  # renBTC
        '0xf9440930043eb3997fc70e1339dbb11f341de7a8': 12463576,  # rETH
        # '0x53a901d48795c58f485cbb38df08fa96a24669d5': 12463570,  # rETH
        '0xeb16ae0052ed37f479f7fe63849198df1765a733': 11772500,  # sAAVE
        # '0x02d341ccb60faaf662bc0554d13778015d1b285c': 11772478,  # sAAVE
        '0x7fc77b5c7614e1533320ea6ddc2eb61fa00a9714': 10276641,  # sBTC
        # '0x075b1bb99792c9e1041ba13afef80c91a1e70fb3': 10276544,  # sBTC
        '0xc5424b857f758e906013f3555dad202e4bdb4567': 11491884,  # sETH
        # '0xa3d87fffce63b53e0d54faa1cc983b7eb0b74a9c': 11491878,  # sETH
        '0xdc24316b9ae028f1497c275eb9192a3ea0f67022': 11592551,  # stETH
        # '0x06325440d014e39736583c165c2963ba99faf14e': 11591275,  # stETH
        # '0xfcba3e75865d2d561be8d220616520c171f12851': 9906734,  # sUSD
        '0xa5407eae9ba41422680e2e00537571bcc53efbfd': 9906598,  # sUSD
        # '0xc25a3a3b969415c80451098fa907ec722572917f': 9906564,  # sUSD
        '0x80466c64868e1ab14a1ddf27a676c3fcbe638fe5': 12521538,  # TriCrypto
        # '0x331af2e331bd619defaa5dac6c038f53fcf9f785': 12602432,  # TriCrypto
        # '0xca3d75ac011bf5ad07a98d02f18225f9bd9a6bdf': 12521516,  # TriCrypto
        # '0xac795d2c97e60df6a99ff1c814727302fd747a80': 9832413,  # USDT
        '0x52ea46506b9cc5ef470c5bf89f17dc28bb35d85c': 9456293,  # USDT
        # '0x9fc689ccada600b6df723d9e47d84d76664a1f23': 9456284,  # USDT
        # '0xbbc81d23ea2c3ec7e56d39296f0cbb648873a5d3': 9832438,  # Y
        '0x45f783cce6b7ff23b2ab2d70e416cdb7d6055f51': 9476468,  # Y
        # '0xdf5e0e81dff6faf3a7e52ba697820c5e32d806a8': 9476452,  # Y
        '0x8925d9d9b4569d737a48499def3f67baa5a144b9': 11784519,  # Yv2
        # '0x571ff5b7b346f706aa48d696a9a4a288e9bb4091': 11784041,  # Yv2
        '0xd51a44d3fae010294c616388b506acda1bfaae46': 12821148,  # tricrypto2
        '0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511': 13676995,  # crveth
        '0xdcef968d416a41cdac0ed8702fac8128a64241a2': 14939588,  # fraxusdc
        '0xc25099792e9349c7dd09759744ea681c7de2cb66': 11095928,  # tbtc
        '0xadcfcf9894335dc340f6cd182afa45999f45fc44': 13854276,  # xautusd
        '0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511': 13676995,  # crveth
        '0xb576491f1e6e5e62f1d8f26062ee822b40b0e0d4': 13783426,  # cvxeth
        # ['reth', '0xf9440930043eb3997fc70e1339dbb11f341de7a8'],  # NOT rocket eth
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
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    factory: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:
    import asyncio
    import pandas as pd

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        provider=provider,
    )

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

    if typing.TYPE_CHECKING:
        events = typing.cast(spec.DataFrame, pd.concat(dfs))
    else:
        events = pd.concat(dfs)

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
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
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
        start_time=start_time,
        end_time=end_time,
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
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    factory: spec.Address | None = None,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:

    import pandas as pd

    if factory is None:
        factory = pool_factory
    if factory == pool_factory:
        factories = [old_pool_factory, pool_factory]
    else:
        factories = [factory]

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        provider=provider,
    )

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

    if typing.TYPE_CHECKING:
        events = typing.cast(spec.DataFrame, pd.concat(dfs))
    else:
        events = pd.concat(dfs)

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
