import asyncio

from ctc import evm
from .. import spec


async def async_compute_dex_volume(blocks, verbose=False):

    volume_tasks = []
    for pool_name, pool_info in spec.dex_pools.items():
        platform = pool_info['platform']
        kwargs = {'pool_address': pool_info['address'], 'blocks': blocks}
        if platform == 'Uniswap V2':
            task = async_compute_uniswap_v2_volume(**kwargs)
        elif platform == 'Uniswap V3':
            task = async_compute_uniswap_v3_volume(**kwargs)
        elif platform == 'Curve':
            task = async_compute_curve_volume(
                fei_index=pool_info['fei_index'],
                event_name=pool_info['event_name'],
                **kwargs
            )
        elif platform == 'Sushi':
            task = async_compute_sushiswap_volume(**kwargs)
        elif platform == 'Saddle':
            fei_index = pool_info['fei_index']
            task = async_compute_saddle_volume(fei_index=fei_index, **kwargs)
        else:
            raise Exception('unknown platform: ' + str())
        volume_tasks.append(asyncio.create_task(task))

    names = list(spec.dex_pools.keys())
    volumes = await asyncio.gather(*volume_tasks)
    volume_by_pool = dict(zip(names, volumes))

    # sum by platform
    volume_by_platform = {}
    for pool_name, pool_info in spec.dex_pools.items():
        pool_volume = volume_by_pool[pool_name]
        platform = pool_info['platform']
        if platform not in volume_by_platform:
            volume_by_platform[platform] = pool_volume
        else:
            assert pool_volume['units'] == volume_by_platform[platform]['units']
            volume_by_platform[platform]['values'] = [
                sum(datapoints)
                for datapoints in zip(
                    pool_volume['values'],
                    volume_by_platform[platform]['values'],
                )
            ]

    return volume_by_platform


async def async_compute_uniswap_v2_volume(pool_address, blocks):
    from ctc.protocols import uniswap_v2_utils

    swaps = await uniswap_v2_utils.async_get_pool_swaps(
        pool_address=pool_address,
        start_block=blocks[0],
        replace_symbols=True,
    )
    fei_sold = evm.bin_by_blocks(swaps['FEI_sold'], blocks)
    fei_bought = evm.bin_by_blocks(swaps['FEI_sold'], blocks)
    return {
        'values': list(fei_sold.values + fei_bought.values),
        'units': 'FEI',
    }


async def async_compute_uniswap_v3_volume(pool_address, blocks):
    import numpy as np
    from ctc.protocols import uniswap_v3_utils

    swaps = await uniswap_v3_utils.async_get_pool_swaps(
        pool_address=pool_address,
        start_block=blocks[0],
        replace_symbols=True,
    )
    binned = evm.bin_by_blocks(np.abs(swaps['FEI_amount']), blocks)
    return {
        'values': list(binned.values),
        'units': 'FEI',
    }


async def async_compute_sushiswap_volume(pool_address, blocks):
    return await async_compute_uniswap_v2_volume(pool_address, blocks)


async def async_compute_curve_volume(
    pool_address, fei_index, event_name, blocks
):

    swaps = evm.get_events(
        contract_address=pool_address,
        event_name=event_name,
        start_block=blocks[0],
    )

    fei_sells = swaps[swaps['arg__sold_id'] == fei_index]
    fei_sold = fei_sells['arg__tokens_sold'].map(float) / 1e18
    fei_buys = swaps[swaps['arg__bought_id'] == fei_index]
    fei_bought = fei_buys['arg__tokens_bought'].map(float) / 1e18

    fei_bought_by_day = evm.bin_by_blocks(data=fei_bought, blocks=blocks)
    fei_sold_by_day = evm.bin_by_blocks(data=fei_sold, blocks=blocks)
    result = fei_bought_by_day + fei_sold_by_day

    return {
        'values': list(result.values),
        'units': 'FEI',
    }


async def async_compute_saddle_volume(pool_address, blocks, fei_index):

    swaps = evm.get_events(
        contract_address=pool_address,
        event_name='TokenSwap',
        start_block=blocks[0],
    )

    fei_sells = swaps[swaps['arg__soldId'] == fei_index]
    fei_sold = fei_sells['arg__tokensSold'].map(float) / 1e18
    fei_buys = swaps[swaps['arg__boughtId'] == fei_index]
    fei_bought = fei_buys['arg__tokensBought'].map(float) / 1e18

    fei_bought_by_day = evm.bin_by_blocks(data=fei_bought, blocks=blocks)
    fei_sold_by_day = evm.bin_by_blocks(data=fei_sold, blocks=blocks)
    result = fei_bought_by_day + fei_sold_by_day

    return {
        'values': list(result.values),
        'units': 'FEI',
    }

