import asyncio

from ctc import rpc
from ctc.protocols import curve_utils


def get_command_spec():
    return {
        'f': async_curve_pools_command,
        'help': 'list curve pools',
        'args': [
            {'name': '--verbose', 'action': 'store_true'},
        ],
    }


async def async_curve_pools_command(verbose):
    factories = [
        '0xB9fC157394Af804a3578134A6585C0dc9cc990d4',
        '0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5',
        '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae',
        '0x8F942C20D02bEfc377D41445793068908E2250D0',
        '0xF18056Bbd320E96A48e3Fbf8bC061322531aac99',
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

    await rpc.async_close_http_session()

