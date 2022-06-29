from __future__ import annotations

import time

import tooltime
import toolstr
import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_timestamp_command,
        'help': 'get block of timestamp',
        'args': [
            {
                'name': 'timestamp',
                'nargs': '?',
                'help': 'timestamp (default = now)',
            },
        ],
        'examples': ['1642114795'],
    }


async def async_timestamp_command(timestamp: str | int) -> None:
    if timestamp is None:
        timestamp = time.time()

    if not isinstance(timestamp, str):
        raise Exception('function input should be str')

    if len(timestamp) == 4 or (
        len(timestamp) == 10 and timestamp.count('-') == 2
    ):
        pass
    else:
        timestamp = int(timestamp)
    timestamp_seconds = tooltime.timestamp_to_seconds(timestamp)
    if timestamp_seconds > time.time():
        print('[predicting future block]')
        print()
        block = await evm.async_predict_timestamp_block(timestamp=timestamp)
    else:
        block = await evm.async_get_block_of_timestamp(timestamp, mode='<=')
    pretty = tooltime.convert_timestamp(timestamp, 'TimestampISO')

    rows = [
        ['ISO time', pretty],
        ['timestamp', str(timestamp_seconds)],
        ['block before', str(block)],
    ]
    toolstr.print_table(rows, column_justify=['right', 'left'])
