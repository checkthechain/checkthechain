import asyncio

from ctc import evm
from ctc.protocols import chainlink_utils
from .. import spec


async def async_compute_prices(blocks, verbose=False):
    feed_data = chainlink_utils.get_feed_data(
        feed_name='FEI_USD', start_block=blocks[0] - 10000
    )
    feed_data = feed_data / 1e8
    feed_data = evm.interpolate_block_series(
        series=feed_data, end_block=blocks[-1]
    )
    result = [feed_data[block] for block in blocks]

    return {
        'USD_FEI Chainlink': {
            'values': result,
            'units': 'USD_FEI',
        },
    }


async def async_compute_pfei_by_deployment(blocks, verbose=False):
    return {
        'Uniswap': {'values': [9999] * len(blocks)},
        'Sushi Swap': {'values': [9999] * len(blocks)},
        'Balancer': {'values': [9999] * len(blocks)},
        'Sushi Kashi': {'values': [9999] * len(blocks)},
        'Ondo': {'values': [9999] * len(blocks)},
        'Rari': {'values': [9999] * len(blocks)},
        'Aave': {'values': [9999] * len(blocks)},
        'Cream': {'values': [9999] * len(blocks)},
        'OA': {'values': [9999] * len(blocks)},
    }


#
# # dex data
#


async def async_compute_dex_tvls(
    blocks: list[int],
    _chunk_by_blocks: bool = False,
    verbose=False,
) -> spec.MetricGroup:

    pools = spec.dex_pools

    names = list(pools.keys())
    addresses = [pool['address'] for pool in pools.values()]

    if _chunk_by_blocks:
        tasks = []
        for block in blocks:
            task = evm.async_get_erc20_balance_of(
                addresses=addresses,
                token='FEI',
                block=block,
            )
            tasks.append(asyncio.create_task(task))
        results = await asyncio.gather(*tasks)
        results = zip(*results)

    else:
        tasks = []
        for address in addresses:
            task = evm.async_get_erc20_balance_of(
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
    for pool_name, pool_info in spec.dex_pools.items():
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

    return tvl_by_platform

