from __future__ import annotations

import json
import os
import time

import toolcli
import toolstr

from ctc.protocols import fei_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_payload_command,
        'help': 'output data payload for app.fei.money/analytics',
        'args': [
            {
                'name': 'timescale',
                'nargs': '?',
                'default': None,
                'help': 'time window size and resolution',
            },
            {'name': '--path', 'help': 'path for data output (a .json file)'},
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'allow overwriting an already-existing file',
            },
        ],
        'examples': {
            '30d,1d': {
                'description': 'create default payload for app.fei.money',
                'runnable': False,
            },
        },
    }


async def async_payload_command(
    *,
    timescale: str,
    path: str,
    overwrite: bool,
) -> None:

    # validate inputs
    if timescale is None:
        timescale = '30d, 1d'
    timescale_full = fei_utils.resolve_timescale(timescale)
    if path is None:
        name = 'payload_{window_size}_{interval_size}'.format(**timescale_full)
        path = './' + name + '.json'

    # print summary
    print('generating data payload')
    print('- interval size:', timescale_full['interval_size'])
    print('- window size:', timescale_full['window_size'])
    print('- output path:', path)

    if os.path.exists(path) and not overwrite:
        raise Exception('path already exists: ' + str(path))

    # create payload
    print()
    print('starting...')
    start_time = time.time()
    payload = await fei_utils.async_create_payload(timescale=timescale_full)
    end_time = time.time()
    print()
    print('...done (t=' + toolstr.format(end_time - start_time) + 's)')

    # save payload
    with open(path, 'w') as f:
        json.dump(payload, f)
