from __future__ import annotations

import typing

from ctc import spec
from ctc.protocols import rari_utils

from .. import yields_spec


hard_min_tvl = 100000
soft_min_tvl = 1000000
hard_min_yield = 0.01
soft_min_yield = 0.001


async def async_get_fei_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, yields_spec.YieldSourceData]:
    """pools must pass both hard mins and at least one soft min"""

    pools = await rari_utils.async_get_all_pools()
    comptrollers = [pool[2] for pool in pools]

    history = await rari_utils.async_get_token_multipool_history(
        token=yields_spec.FEI,
        blocks=block_numbers,
        metrics={'supply_apy': True, 'tvl': True},
        comptrollers=comptrollers,
    )

    # filter pools
    filtered = {}
    for comptroller, pool_data in history.items():
        pass_hard_min_tvl = any(
            number > hard_min_tvl for number in pool_data['tvl']
        )
        pass_soft_min_tvl = any(
            number > soft_min_tvl for number in pool_data['tvl']
        )
        pass_hard_min_yield = any(
            number > hard_min_yield for number in pool_data['tvl']
        )
        pass_soft_min_yield = any(
            number > soft_min_yield for number in pool_data['tvl']
        )
        if (
            pass_hard_min_tvl
            and pass_hard_min_yield
            and (pass_soft_min_tvl and pass_soft_min_yield)
        ):
            filtered[comptroller] = pool_data
    history = filtered

    # format as output
    output: dict[str, yields_spec.YieldSourceData] = {}
    for comptroller, pool_data in history.items():
        index = comptrollers.index(comptroller)
        name = 'Rari Pool ' + str(index)
        output[name] = {
            # metadata
            'name': name,
            'url': 'https://app.rari.capital/fuse/pool/' + str(index),
            'category': 'Lending',
            'platform': 'Rari',
            'staked_tokens': [yields_spec.FEI],
            'reward_tokens': [yields_spec.FEI],
            #
            # metrics
            'tvl_history': pool_data['tvl'],
            'tvl_history_units': 'USD',
            'current_yield': {'Spot': pool_data['supply_apy'][0]},
            'current_yield_units': {'Spot': 'APY'},
            'yield_history': {'Lending Interest': pool_data['supply_apy']},
            'yield_history_units': {'Lending Interest': 'APY'},
        }

    return output

