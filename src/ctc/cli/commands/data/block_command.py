from __future__ import annotations

import toolcli

from ctc import evm
from ctc import rpc


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_block_command,
        'help': 'summarize block',
        'args': [
            {'name': 'block', 'nargs': '?', 'help': 'block number'},
            {
                'name': '--timestamp',
                'type': int,
                'help': 'specify block by timestamp',
            },
            {
                'name': '--verbose',
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
        'examples': [
            '14000000',
            '14000000 --json',
            '--timestamp 1600000000',
        ],
    }


async def async_block_command(
    block: str | None,
    timestamp: int,
    verbose: bool,
    as_json: bool,
) -> None:

    if block is None:
        if timestamp is not None:
            print('searching for block at timestamp:', timestamp)
            block_number = await evm.async_get_block_of_timestamp(
                timestamp=timestamp,
                verbose=False,
            )
            print('found block', block)
            print()
        else:
            raise Exception('must specify block or timestamp')
    else:
        block_number = await evm.async_block_number_to_int(block)

    if as_json:
        import rich
        import json

        block_data = await evm.async_get_block(block_number)
        rich.print_json(json.dumps(block_data))
    else:
        await evm.async_print_block_summary(block=block_number)

    await rpc.async_close_http_session()

