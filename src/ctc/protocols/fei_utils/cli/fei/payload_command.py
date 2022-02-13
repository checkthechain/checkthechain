import asyncio
import json
import os
import time

import toolstr

from ctc import rpc
from ctc.protocols import fei_utils


def get_command_spec():
    return {
        'f': async_payload_command,
        'args': [
            {'name': 'timescale', 'kwargs': {'nargs': '?', 'default': None}},
            {'name': '--path'},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
        ],
    }


async def async_payload_command(timescale, path, overwrite, **kwargs):

    # validate inputs
    if timescale is None:
        timescale = '30d, 1d'
    timescale = fei_utils.resolve_timescale(timescale)
    if path is None:
        name = 'payload_{window_size}_{interval_size}'.format(**timescale)
        path = './' + name + '.json'

    # print summary
    print('generating data payload')
    print('- interval size:', timescale['interval_size'])
    print('- window size:', timescale['window_size'])
    print('- output path:', path)

    if os.path.exists(path) and not overwrite:
        raise Exception('path already exists: ' + str(path))

    # create payload
    print()
    print('starting...')
    start_time = time.time()
    payload = await fei_utils.async_create_payload(timescale=timescale)
    end_time = time.time()
    print()
    print('...done (t=' + toolstr.format(end_time - start_time) + 's)')

    # save payload
    with open(path, 'w') as f:
        json.dump(payload, f)

    provider = rpc.get_provider()
    await rpc.async_close_http_session(provider=provider)

