import asyncio

from ctc import evm
from .. import spec


async def async_compute_prices(blocks, verbose=False):
    return {
        'FEI_USD': [9999] * len(blocks),
    }


async def async_compute_circulating_fei(blocks, verbose=False):
    return {
        'pfei': [9999] * len(blocks),
        'ufei': [9999] * len(blocks),
    }


async def async_compute_pfei_by_deployment(blocks, verbose=False):
    return {
        'Uniswap': [9999] * len(blocks),
        'Sushi Swap': [9999] * len(blocks),
        'Balancer': [9999] * len(blocks),
        'Sushi Kashi': [9999] * len(blocks),
        'Ondo': [9999] * len(blocks),
        'Rari': [9999] * len(blocks),
        'Aave': [9999] * len(blocks),
        'Cream': [9999] * len(blocks),
        'OA': [9999] * len(blocks),
    }


#
# # dex data
#


async def async_compute_dex_tvls(
    blocks: list[int],
    _chunk_by_blocks: bool = False,
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

    tvls_by_pool = dict(zip(names, results))

    return {
        pool: {'values': tvl, 'units': 'FEI', 'name': pool}
        for pool, tvl in tvls_by_pool.items()
    }


async def async_compute_dex_volume(blocks, verbose=False):
    volume_tasks = []
    for pool_name, pool_info in spec.dex_pools.items():
        platform = pool_info['platform']
        kwargs = {'address': pool_info['address'], 'blocks': blocks}
        if platform == 'uniswap_v2':
            task = async_compute_uniswap_v2_volume(**kwargs)
        elif platform == 'uniswap_v3':
            task = async_compute_uniswap_v3_volume(**kwargs)
        elif platform == 'curve':
            task = async_compute_curve_volume(**kwargs)
        elif platform == 'sushi':
            task = async_compute_sushi_volume(**kwargs)
        elif platform == 'saddle':
            task = async_compute_saddle_volume(**kwargs)
        else:
            raise Exception('unknown platform: ' + str())
        volume_tasks.append(asyncio.create_task(task))

    names = list(spec.dex_pools.keys())
    volumes = await asyncio.gather(volume_tasks)
    volume_by_pool = dict(zip(names, volumes))

    return volume_by_pool


async def async_compute_uniswap_v2_volume(address, blocks):
    from ctc.protocols import uniswap_v2_utils

    swaps = await uniswap_v2_utils.async_get_pool_swaps(
        pool_address=address, start_block=blocks[0], replace_symbols=True,
    )
    binned = evm.bin_by_blocks(swaps, blocks)
    return {
        'values': (binned['FEI_sold'] + binned['FEI_bought']),
        'units': 'FEI',
    }


async def async_compute_uniswap_v3_volume(address, blocks):
    import numpy as np
    from ctc.protocols import uniswap_v3_utils

    swaps = await uniswap_v3_utils.async_get_pool_swaps(
        pool_address=address, start_block=blocks[0], replace_symbols=True,
    )
    binned = evm.bin_by_blocks(np.abs(swaps['FEI_amount']), blocks)
    return {
        'values': list(binned.values),
        'units': 'FEI',
    }

