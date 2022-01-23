import asyncio
import math

import toolstr
import tooltime
import tooltable  # type: ignore

from ctc import directory
from ctc import rpc
from ctc.protocols import chainlink_utils
from . import fuse_queries


display_names = {
    'Tetranode\'s Flavor of the Month': 'FeiRari (Fei DAO Pool)',
    'Frax & Reflexer Stable Asset Pool': 'FRAX RAI Stable Pool',
}


def sort_nested_by(nested, key, reverse=False):
    pairs = list(nested.items())
    sorted_pairs = sorted(pairs, key=lambda pair: pair[1][key], reverse=reverse)
    return dict(sorted_pairs)


def print_fuse_pool_summary(block, *, tokens_data, pool_name):

    tvl = sum(token_data['supplied'] for token_data in tokens_data.values())
    tvb = sum(token_data['borrowed'] for token_data in tokens_data.values())

    # get block data
    block_number = block['number']
    time_iso = tooltime.timestamp_to_iso(block['timestamp']).replace('T', ' ')

    headers = {
        'name': 'token',
        'supplied_tvl': 'TVL',
        'borrowed_tvl': 'TVB',
        'liquidity_tvl': 'liquidity',
        'supply_apy': 'supply %',
        'borrow_apy': 'borrow %',
        'utilization': 'util %',
    }

    tokens_data = sort_nested_by(tokens_data, 'supplied_tvl', reverse=True)

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
    # print('- time:', time_iso)
    print()
    tooltable.print_table(rows, headers=headers.values())


async def print_all_pool_summary(block='latest', n_display=15):

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

    total_tvl = 0
    total_tvb = 0

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

        total_tvl += pool_stats['tvl']
        total_tvb += pool_stats['tvb']

        name = pool[0]
        name = display_names.get(pool[0], pool[0])

        row.append(all_pools.index(pool))
        row.append(name)
        row.append(tvl)
        row.append(tvb)
        rows.append(row)

    block_data = await rpc.async_eth_get_block_by_number(block)
    timestamp = tooltime.timestamp_to_iso(block_data['timestamp']).replace(
        'T', ' '
    )

    toolstr.print_header('Rari Fuse')
    print(
        '- TVL:', toolstr.format(total_tvl, prefix='$', order_of_magnitude=True)
    )
    print(
        '- TVB:', toolstr.format(total_tvb, prefix='$', order_of_magnitude=True)
    )
    print('- block:', block)
    # print('- time:', timestamp)
    print()
    tooltable.print_table(rows, headers=['#', 'pool', 'TVL', 'TVB'])


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


async def async_get_token_multipool_stats(token, block='latest', in_usd=True):
    pools = await fuse_queries.async_get_all_pools(block=block)

    eth_price = await chainlink_utils.async_get_eth_price(block=block)
    pools_stats = [
        asyncio.create_task(
            async_get_token_pool_stats(
                token=token,
                comptroller=pool[2],
                eth_price=eth_price,
                block=block,
                in_usd=in_usd,
            )
        )
        for pool in pools
    ]
    pools_stats = await asyncio.gather(*pools_stats)
    tvl = 0
    tvb = 0
    for pool_stats in pools_stats:
        tvl += pool_stats['tvl']
        tvb += pool_stats['tvb']

    comptrollers = [pool[2] for pool in pools]
    per_pool = dict(zip(comptrollers, pools_stats))

    per_pool = sorted(
        per_pool.items(), key=lambda item: item[1]['tvl'], reverse=True
    )
    per_pool = dict(per_pool)

    pool_names = [
        asyncio.create_task(
            fuse_queries.async_get_pool_name(
                comptroller=comptroller, all_pools=pools
            )
        )
        for comptroller in per_pool.keys()
    ]

    per_pool = {k: v for k, v in per_pool.items() if v['ctoken'] is not None}
    if len(per_pool) > 0:
        blocks_per_year = None
        for p, (comptroller, pool_stats) in enumerate(per_pool.items()):

            irm = await fuse_queries.async_get_ctoken_irm(
                ctoken=pool_stats['ctoken'],
                block=block,
            )
            blocks_per_year = await fuse_queries.async_get_irm_blocks_per_year(
                irm,
                block=block,
            )

            pool_stats['supply_apy'] = await fuse_queries.async_get_supply_apy(
                ctoken=pool_stats['ctoken'],
                block=block,
                blocks_per_year=blocks_per_year,
            )
            pool_stats['borrow_apy'] = await fuse_queries.async_get_borrow_apy(
                ctoken=pool_stats['ctoken'],
                block=block,
                blocks_per_year=blocks_per_year,
            )

            pool_stats['name'] = await pool_names[p]

            # get pool index
            for pool_index, pool in enumerate(pools):
                if pool[2] == comptroller:
                    pool_stats['pool_index'] = pool_index
                    break
            else:
                raise Exception('could not detect pool index')

    return {
        'total': {'tvl': tvl, 'tvb': tvb},
        'per_pool': per_pool,
    }


async def async_get_token_pool_stats(
    token, comptroller, eth_price, block='latest', in_usd=True,
):

    ctokens = await fuse_queries.async_get_pool_ctokens(
        comptroller=comptroller, block=block
    )
    underlyings = await fuse_queries.async_get_pool_underlying_tokens(
        ctokens=ctokens, block=block
    )
    oracle = await fuse_queries.async_get_pool_oracle(
        comptroller=comptroller, block=block
    )

    tvl = 0
    tvb = 0
    matches = []
    for ctoken, underlying in underlyings.items():
        if underlying == token:
            matches.append(ctoken)
            stats = await fuse_queries.async_get_ctoken_tvl_and_tvb(
                ctoken,
                oracle,
                eth_price,
                block=block,
                in_usd=in_usd,
            )
            tvl += stats['tvl']
            tvb += stats['tvb']

    if len(matches) > 0:
        ctoken = matches[0]
    else:
        ctoken = None

    return {'tvl': tvl, 'tvb': tvb, 'ctoken': ctoken, 'matches': matches}


async def async_print_fuse_token_summary(token, block='latest', in_usd=True):

    if directory.has_erc20_metadata(symbol=token):
        token = directory.get_erc20_address(symbol=token)
    if token == '0x0000000000000000000000000000000000000000':
        symbol = 'ETH'
    else:
        symbol = directory.get_erc20_symbol(token)

    block = await rpc.async_eth_get_block_by_number(block)
    multipool_stats = await async_get_token_multipool_stats(
        token,
        block=block['number'],
        in_usd=in_usd,
    )

    if in_usd:
        prefix = '$'
    else:
        prefix = None

    include_empty = False

    headers = [
        'pool',
        'TVL',
        'TVB',
        'supply %',
        'borrow %',
        'util %',
    ]
    rows = []
    for pool_stats in multipool_stats['per_pool'].values():
        if math.isclose(pool_stats['tvl'], 0):

            if not include_empty:
                continue

            util = 0
        else:
            util = pool_stats['tvb'] / pool_stats['tvl']
        row = [
            pool_stats['name'],
            toolstr.format(
                pool_stats['tvl'], order_of_magnitude=True, prefix=prefix
            ),
            toolstr.format(
                pool_stats['tvb'], order_of_magnitude=True, prefix=prefix
            ),
            toolstr.format(pool_stats['supply_apy'], percentage=True),
            toolstr.format(pool_stats['borrow_apy'], percentage=True),
            toolstr.format(util, percentage=True),
        ]
        rows.append(row)

    tvl = 0
    tvb = 0
    for pool_stats in multipool_stats['per_pool'].values():
        tvl += pool_stats['tvl']
        tvb += pool_stats['tvb']
    timestamp = tooltime.timestamp_to_iso(block['timestamp']).replace('T', ' ')

    toolstr.print_header(symbol + ' Token Fuse Usage')
    print('- TVL:', toolstr.format(tvl, order_of_magnitude=True, prefix=prefix))
    print('- TVB:', toolstr.format(tvb, order_of_magnitude=True, prefix=prefix))
    print('- block:', block['number'])
    # print('- time:', timestamp)
    print()
    tooltable.print_table(rows, headers=headers)

