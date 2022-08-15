from __future__ import annotations

import time

import toolcli
import tooltime

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_block_command,
        'help': 'summarize block',
        'args': [
            {'name': 'block', 'nargs': '?', 'help': 'block number'},
            {
                'name': '--timestamp',
                'help': 'specify block by timestamp',
            },
            {
                'name': ['--verbose', '-v'],
                'action': 'store_true',
                'help': 'emit extra information',
            },
            {
                'name': '--json',
                'help': 'output block as raw json',
                'dest': 'as_json',
                'action': 'store_true',
            },
        ],
        'extra_data': ['parse_spec'],
        'examples': [
            '14000000',
            '14000000 --json',
            '--timestamp 1600000000',
        ],
    }


async def async_block_command(
    *,
    block: str | None,
    timestamp: str | int,
    verbose: bool,
    as_json: bool,
    parse_spec: toolcli.ParseSpec,
) -> None:

    if block is None:
        if timestamp is not None:

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
                block_number = await evm.async_predict_timestamp_block(
                    timestamp
                )
                print('predicting future block...')
                print(block_number)
                return
            else:
                print('searching for block at timestamp:', timestamp)
                block_number = await evm.async_get_block_of_timestamp(
                    timestamp=timestamp,
                    verbose=False,
                )
                print('found block', block_number)
                print()
        else:
            block_number = 'latest'
    else:
        block_number = await evm.async_block_number_to_int(block)

    if as_json:
        import rich
        import json

        block_data = await evm.async_get_block(
            block_number,
            include_full_transactions=False,
        )
        rich.print_json(json.dumps(block_data))
    else:
        await evm.async_print_block_summary(block=block_number)
