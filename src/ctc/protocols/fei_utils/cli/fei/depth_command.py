from __future__ import annotations

import json

from ctc import rpc

import toolstr
import tooltable

from ctc.protocols import fei_utils


def get_command_spec():
    return {
        'f': async_depth_command,
        'help': 'output FEI liquidity depth information',
        'args': [
            {
                'name': '--prices',
                'help': 'specify which price levels to output depths of',
            },
            {
                'name': '--json',
                'help': 'output data as json',
                'dest': 'as_json',
                'action': 'store_true',
            },
        ],
    }


async def async_depth_command(prices, as_json):

    if prices is None:
        prices = [
            0.995,
            0.993,
            0.990,
        ]

    pool_price_depth = await fei_utils.async_get_fei_uniswap_pool_price_depth(
        prices=prices
    )

    if as_json:
        content = json.dumps(pool_price_depth, sort_keys=True, indent=True)
        print(content)
    else:
        rows = []
        for pool in pool_price_depth.keys():
            row = [pool]
            for price in prices:
                value = pool_price_depth[pool][price] / 1e18
                row.append(
                    toolstr.format(value, order_of_magnitude=True, prefix='$')
                )
            rows.append(row)

        headers = ['pool'] + ['to $' + str(price) for price in prices]
        toolstr.print_text_box('FEI Liquidity Depth')
        print()
        print(
            'depth shown = amount of FEI sold before DEX price reaches target value'
        )
        print('(this is different from the realized price for these trades)')
        print()
        tooltable.print_table(rows, headers=headers)

    await rpc.async_close_http_session()

