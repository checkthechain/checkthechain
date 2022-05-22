from __future__ import annotations

import time

import tooltime
import toolstr
import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': timestamp_command,
        'help': 'get block of timestamp',
        'args': [
            {
                'name': 'timestamp',
                'nargs': '?',
                'help': 'timestamp (default = now)',
            },
        ],
    }


async def timestamp_command(timestamp: str) -> None:
    if timestamp is None:
        timestamp = time.time()

    timestamp_int = int(timestamp)
    pretty = tooltime.convert_timestamp(timestamp_int, 'TimestampISO')
    block = await evm.async_get_block_of_timestamp(timestamp_int, mode='before')

    rows = [
        ['ISO time', pretty],
        ['timestamp', str(timestamp_int)],
        ['block before', str(block)],
    ]
    toolstr.print_table(rows, column_justify=['right', 'left'])
