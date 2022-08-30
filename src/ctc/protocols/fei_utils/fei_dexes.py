"""TODO: generalize these functions to any ERC20"""

from __future__ import annotations

from typing_extensions import TypedDict

import typing

from ctc import evm
from ctc import spec


address_pools = {
    '0xba12222222228d8ba445958a75a0704d566bf2c8': 'Balancer Vault',
    '0xbaaa1f5dba42c3389bdbc2c9d2de134f5cd0dc89': 'Curve D3',
    '0x06cb22615ba53e60d67bf6c341a0fd5e718e1655': 'Curve FEI-3CRV',
    '0xc69ddcd4dfef25d8a793241834d4cc4b3668ead6': 'Saddle D4',
    '0x9928e4046d7c6513326ccea028cd3e7a91c7590a': 'Uniswap V2: TRIBE-FEI',
    '0xf89ce5ed65737da8440411544b0499c9fad323b2': 'Uniswap V2: FEI-agEUR',
    '0xbeddb932490e776301c776526615965fae2440de': 'Uniswap V2: FEI-FOX',
    '0xeb9609fa6846d028b80140edc16db4d911562c1e': 'Uniswap V2: VOLT-FEI',
    '0x94b0a3d511b6ecdb17ebf877278ab030acb0a878': 'Uniswap V2: FEI-ETH',
    '0x58664dbfcd772a6f442c1b4e6780446c51d73103': 'Uniswap V2: GRO-FEI',
    '0xce29c85c5a4fc2fa5cc4f681d4d1527a656ba399': 'Uniswap V2: FEI-NEAR',
    '0x0f024314588466416c8fc66013ba4d3ab2e4efe5': 'Uniswap V2: UMA-FEI',
    '0x9e2336aef4157944f201becd90ccb24e298660cb': 'Uniswap V2: SYN-FEI',
    '0x5d62134dbd7d56fae9bc0b7df3788f5f8dade62d': 'Uniswap V2: POOL-FEI',
    '0x9241943c29eb0b1fc0f8e5b464fbc14915da9a57': 'Uniswap V2: FEI-MTA',
    '0x7977853de0700d121f30bfd7ea127d8f6297084b': 'Uniswap V2: KYL-FEI',
    '0xdf50fbde8180c8785842c8e316ebe06f542d3443': 'Uniswap V3: FEI-USDC 0.01%',
    '0x8c54aa2a32a779e6f6fbea568ad85a19e0109c26': 'Uniswap V3: FEI-USDC 0.05%',
    '0xbb2e5c2ff298fd96e166f90c8abacaf714df14f8': 'Uniswap V3: FEI-DAI 0.05%',
    '0x063c3ad01e6449383788d2047104654ff4c8db05': 'Uniswap V3: FEI-UST 0.05%',
    '0x8775ae5e83bc5d926b6277579c2b0d40c7d9b528': 'SushiSwap DPI-FEI',
}
pools = {v: k for k, v in address_pools.items()}


pool_tokens = {
    'Curve FEI-3CRV': ['FEI', '3CRV'],
    'Curve D3': ['FEI', 'FRAX', 'alUSD'],
    'Saddle D4': ['FEI', 'FRAX', 'LUSD', 'alUSD'],
    'Uniswap V3: FEI-USDC 0.01%': ['FEI', 'USDC'],
    'Uniswap V3: FEI-USDC 0.05%': ['FEI', 'USDC'],
    'Uniswap V3: FEI-DAI 0.05%': ['FEI', 'DAI'],
}

pool_colors = {
    'Curve FEI-3CRV': 'tomato',
    'Curve D3': 'firebrick',
    'Saddle D4': 'purple',
    'Uniswap V3: FEI-USDC 0.01%': 'darkturquoise',
    'Uniswap V3: FEI-USDC 0.05%': 'blue',
    'Uniswap V3: FEI-DAI 0.05%': 'goldenrod',
}


def get_token_map() -> dict[str, spec.Address]:
    return {
        'FEI': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        'LUSD': '0x5f98805a4e8be255a32880fdec7f6728c6568ba0',
        'alUSD': '0xbc6da0fe9ad5f3b0d58160288917aa56653660e9',
        'FRAX': '0x853d955acef822db058eb8505911ed77f175b99e',
        'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f',
        'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
        '3CRV': '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490',
    }


async def async_get_stable_dex_balances_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, spec.NumpyArray]:
    import asyncio
    import numpy as np

    token_map = get_token_map()

    coroutines = {}
    for pool_name in pool_tokens.keys():
        for token in pool_tokens[pool_name]:
            label = pool_name + '__' + token
            coroutines[label] = evm.async_get_erc20_balance_by_block(
                wallet=pools[pool_name],
                token=token_map[token],
                blocks=blocks,
            )

    results = await asyncio.gather(*coroutines.values())
    pool_balances = dict(zip(coroutines.keys(), results))
    pool_balances = {
        key: np.array(value) for key, value in pool_balances.items()
    }

    return pool_balances


class FEIDEXMetrics(TypedDict):
    pool_balances: typing.Mapping[str, spec.NumpyArray]
    total_FEI: spec.NumpyArray
    pool_tvls: typing.Mapping[str, spec.NumpyArray]
    total_tvl: spec.NumpyArray
    pool_imbalances: typing.Mapping[str, spec.NumpyArray]
    total_imbalance: spec.NumpyArray


async def async_get_fei_stable_dex_metrics_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference] | None = None,
    pool_balances: typing.Mapping[str, spec.NumpyArray] | None = None,
) -> FEIDEXMetrics:

    if pool_balances is None:
        if blocks is None:
            raise Exception('must specify blocks or pool_balances')
        pool_balances = await async_get_stable_dex_balances_by_block(
            blocks=blocks
        )

    pool_tvls: typing.MutableMapping[str, spec.NumpyArray] = {}
    pool_targets = {}
    pool_fei_tvls = {}
    pool_fei_imbalances: typing.MutableMapping[str, spec.NumpyArray] = {}
    for pool_name in pool_tokens.keys():

        # pool tvls
        pool_token_balances = [
            pool_balances[pool_name + '__' + token]
            for token in pool_tokens[pool_name]
        ]

        value = sum(pool_token_balances)
        if typing.TYPE_CHECKING:
            pool_tvls[pool_name] = typing.cast(spec.NumpyArray, value)
        else:
            pool_tvls[pool_name] = value
        # pool targets
        n_tokens = len(pool_tokens[pool_name])
        pool_targets[pool_name] = pool_tvls[pool_name] / n_tokens

        # pool imbalances
        pool_fei_tvls[pool_name] = pool_balances[pool_name + '__FEI']
        pool_fei_imbalances[pool_name] = (
            pool_fei_tvls[pool_name] - pool_targets[pool_name]
        )

    if typing.TYPE_CHECKING:
        total_pool_tvls = typing.cast(spec.NumpyArray, sum(pool_tvls.values()))
        total_pool_fei_tvl = typing.cast(
            spec.NumpyArray, sum(pool_fei_tvls.values())
        )
        total_pool_fei_imbalance = typing.cast(
            spec.NumpyArray, sum(pool_fei_imbalances.values())
        )
    else:
        total_pool_tvls = sum(pool_tvls.values())
        total_pool_fei_tvl = sum(pool_fei_tvls.values())
        total_pool_fei_imbalance = sum(pool_fei_imbalances.values())

    return {
        'pool_balances': pool_balances,
        'total_FEI': total_pool_fei_tvl,
        'pool_tvls': pool_tvls,
        'total_tvl': total_pool_tvls,
        'pool_imbalances': pool_fei_imbalances,
        'total_imbalance': total_pool_fei_imbalance,
    }
