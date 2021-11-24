import asyncio
import math

import toolstr
import tooltime
import tooltable

from ctc import rpc
from . import fuse_queries


display_names = {
    'Tetranode\'s Flavor of the Month': 'FeiRari (Fei DAO Pool)',
}


def print_fuse_pool_summary(block, *, tokens_data, pool_name):

    tvl = sum(token_data['supplied'] for token_data in tokens_data.values())
    tvb = sum(token_data['borrowed'] for token_data in tokens_data.values())

    # get block data
    block_number = block['number']
    time_iso = tooltime.timestamp_to_iso(block['timestamp']).replace('T', ' ')

    headers = {
        'name': 'token',
        'supplied_tvl': 'supplied',
        'borrowed_tvl': 'borrowed',
        'liquidity_tvl': 'liquidity',
        'supply_apy': 'supply %',
        'borrow_apy': 'borrow %',
        'utilization': 'util %',
    }

    rows = []

    for token_name, token_data in tokens_data.items():
        row = []
        for column in headers:
            datum = token_data[column]
            if column in ['utilization', 'supply_apy', 'borrow_apy']:
                datum = toolstr.format(datum, percentage=True, decimals=2)
            elif isinstance(datum, (int, float)):
                datum = toolstr.format(
                    datum,
                    prefix='$',
                    order_of_magnitude=True,
                )
            row.append(datum)
        rows.append(row)

    if pool_name in display_names:
        pool_name = display_names[pool_name]
    toolstr.print_header(pool_name)
    print('- TVL:', toolstr.format(tvl, prefix='$', order_of_magnitude=True))
    print('- TVB:', toolstr.format(tvb, prefix='$', order_of_magnitude=True))
    print('- block:', block_number)
    print('- time:', time_iso)
    print()
    tooltable.print_table(rows, headers=headers.values())


async def print_all_pool_summary(block='latest', n_display=10):

    if block == 'latest':
        block = await rpc.async_eth_block_number()

    all_pools = await fuse_queries.async_get_all_pools(block=block)

    pools_stats = await _async_get_all_pools_stats(all_pools, block=block)

    stats_by_comptroller = {
        pool[2]: pool_stats for pool, pool_stats in zip(all_pools, pools_stats)
    }

    sorted_pools = sorted(
        all_pools[: len(stats_by_comptroller)],
        key=lambda pool: stats_by_comptroller[pool[2]]['tvl'],
        reverse=True,
    )

    rows = []
    for pool in sorted_pools[:n_display]:

        pool_stats = stats_by_comptroller[pool[2]]

        row = []

        tvb = toolstr.format(
            pool_stats['tvb'], order_of_magnitude=True, prefix='$'
        )
        tvl = toolstr.format(
            pool_stats['tvl'], order_of_magnitude=True, prefix='$'
        )

        name = pool[0]
        name = display_names.get(pool[0], pool[0])

        row.append(all_pools.index(pool))
        row.append(name)
        row.append(tvb)
        row.append(tvl)
        rows.append(row)

    print('Top ' + str(n_display) + ' Fuse Pools By TVL')
    print()
    tooltable.print_table(rows, headers=['#', 'pool', 'TVB', 'TVL'])


async def _async_get_all_pools_stats(all_pools, block):

    n_pools = len(all_pools)
    chunk_size = 300
    n_chunks = math.ceil(n_pools / chunk_size)

    pools_stats = []
    for c in range(n_chunks):

        # print('chunk', c + 1, '/', n_chunks)

        chunk_pools = all_pools[slice(c * chunk_size, (c + 1) * chunk_size)]
        # print(slice(c * chunk_size, (c + 1) * chunk_size))

        chunk_pools_stats = [
            asyncio.create_task(
                fuse_queries.get_pool_tvl_and_tvb(
                    comptroller=pool[2], block=block
                )
            )
            for pool in chunk_pools
        ]

        chunk_pools_stats = await asyncio.gather(*chunk_pools_stats)

        pools_stats += chunk_pools_stats

    return pools_stats

