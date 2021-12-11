import asyncio
import typing

from ctc import evm
from ctc.protocols import chainlink_utils
from .. import analytics_spec


async def async_compute_prices(
    blocks: list[int], verbose: bool = False
) -> analytics_spec.MetricGroup:
    feed_data = chainlink_utils.get_feed_data(
        feed_name='FEI_USD', start_block=blocks[0] - 10000
    )
    feed_data = feed_data / 1e8
    feed_data = evm.interpolate_block_series(
        series=feed_data, end_block=blocks[-1]
    )
    result = [feed_data[block] for block in blocks]

    return {
        'name': 'Prices',
        'metrics': [
            {
                'name': 'USD_FEI Chainlink',
                'values': result,
                'units': 'USD_FEI',
            },
        ],
    }


async def async_compute_pfei_by_deployment(
    blocks: list[int], verbose: bool = False
) -> analytics_spec.MetricGroup:
    return {
        'name': 'Protocol FEI Deployments',
        'metrics': [
            {'name': 'Uniswap', 'values': [9999] * len(blocks)},
            {'name': 'Sushi Swap', 'values': [9999] * len(blocks)},
            {'name': 'Balancer', 'values': [9999] * len(blocks)},
            {'name': 'Sushi Kashi', 'values': [9999] * len(blocks)},
            {'name': 'Ondo', 'values': [9999] * len(blocks)},
            {'name': 'Rari', 'values': [9999] * len(blocks)},
            {'name': 'Aave', 'values': [9999] * len(blocks)},
            {'name': 'Cream', 'values': [9999] * len(blocks)},
            {'name': 'OA', 'values': [9999] * len(blocks)},
        ],
    }


#
# # dex data
#


async def async_compute_dex_tvls(
    blocks: list[int],
    verbose: bool = False,
) -> analytics_spec.MetricGroup:

    pools = analytics_spec.dex_pools

    names = list(pools.keys())
    addresses = [pool['address'] for pool in pools.values()]

    _chunk_by_blocks = False
    if _chunk_by_blocks:
        tasks: list[asyncio.Task[typing.Union[list[int], list[float]]]] = []
        for block in blocks:
            task = evm.async_get_erc20_balance_of_addresses(
                addresses=addresses,
                token='FEI',
                block=block,
            )
            tasks.append(asyncio.create_task(task))
        results = await asyncio.gather(*tasks)
        results = list(zip(*results))

    else:
        tasks = []
        for address in addresses:
            task = evm.async_get_erc20_balance_of_by_block(
                address=address,
                token='FEI',
                blocks=blocks,
            )
            tasks.append(asyncio.create_task(task))
        results = await asyncio.gather(*tasks)

    tvl_by_pool = dict(zip(names, results))

    tvl_by_pool = {
        pool: {'values': tvl, 'units': 'FEI', 'name': pool}
        for pool, tvl in tvl_by_pool.items()
    }

    # sum by platform
    tvl_by_platform = {}
    for pool_name, pool_info in analytics_spec.dex_pools.items():
        pool_tvl = tvl_by_pool[pool_name]
        platform = pool_info['platform']
        if platform not in tvl_by_platform:
            tvl_by_platform[platform] = pool_tvl
        else:
            assert pool_tvl['units'] == tvl_by_platform[platform]['units']
            tvl_by_platform[platform]['values'] = [
                sum(datapoints)
                for datapoints in zip(
                    pool_tvl['values'],
                    tvl_by_platform[platform]['values'],
                )
            ]

    metrics = list(tvl_by_platform.values())

    return {
        'name': 'DEX TVL by Platform',
        'metrics': metrics,
    }

