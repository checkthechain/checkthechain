from __future__ import annotations

import json
import typing

import toolcli
import toolstr

from ctc.protocols import fei_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_depth_command,
        'help': 'output FEI liquidity depth information',
        'args': [
            {
                'name': '--prices',
                'help': 'specify which price levels to output depths of',
                'nargs': '+',
            },
            {
                'name': '--json',
                'help': 'output data as json',
                'dest': 'as_json',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            '--prices "0.996" "0.997"',
        ],
    }


async def async_depth_command(
    prices: typing.Sequence[str], as_json: bool
) -> None:

    if prices is None:
        prices_float = [
            0.995,
            0.993,
            0.990,
        ]
    else:
        prices_float = [float(price) for price in prices]

    pool_price_depth = await fei_utils.async_get_fei_uniswap_pool_price_depth(
        prices=prices_float
    )

    if as_json:
        content = json.dumps(pool_price_depth, sort_keys=True, indent=True)
        print(content)
    else:
        rows = []
        for pool in pool_price_depth.keys():
            row: list[typing.Any] = [pool]
            for price in prices_float:
                value = pool_price_depth[pool][price] / 1e18
                row.append(value)
            rows.append(row)

        labels = ['pool'] + ['to $' + str(price) for price in prices_float]
        toolstr.print_text_box('FEI Liquidity Depth')
        print()
        print(
            'depth shown = amount of FEI sold before DEX price reaches target value'
        )
        print('(this is different from the realized price for these trades)')
        print()
        toolstr.print_table(
            rows,
            labels=labels,
            format={
                'order_of_magnitude': True,
                'prefix': '$',
                'decimals': 2,
                'trailing_zeros': True,
            },
        )
