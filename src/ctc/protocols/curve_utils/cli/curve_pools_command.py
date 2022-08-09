from __future__ import annotations


import toolcli

from ctc.protocols import curve_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_curve_pools_command,
        'help': 'list curve pools',
        'args': [
            {
                'name': ['--verbose', '-v'],
                'help': 'include extra data',
                'action': 'store_true',
            },
        ],
        'examples': ['', '--verbose'],
    }


async def async_curve_pools_command(verbose: bool) -> None:
    import asyncio

    factories = [
        '0xb9fc157394af804a3578134a6585c0dc9cc990d4',
        '0x90e00ace148ca3b23ac1bc8c240c2a7dd9c2d7f5',
        '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae',
        '0x8f942c20d02befc377d41445793068908e2250d0',
        '0xf18056bbd320e96a48e3fbf8bc061322531aac99',
    ]

    # get data from each factory
    coroutines = [
        curve_utils.async_get_factory_pool_data(factory, include_balances=False)
        for factory in factories
    ]
    factories_data = await asyncio.gather(*coroutines)
    items = [item for factory_data in factories_data for item in factory_data]

    # print as table
    completed = set()
    items = sorted(items, key=lambda item: ', '.join(item['symbols']))
    for item in items:

        if item['address'] in completed:
            continue
        else:
            completed.add(item['address'])

        if not verbose:
            skip = False
            for symbol in item['symbols']:
                if symbol.startswith('RC_'):
                    skip = True
            if skip:
                continue

        print(item['address'] + '    ' + ', '.join(item['symbols']))
