from ctc import evm
from ctc import rpc


def get_command_spec():
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
            }
        ],
    }


async def async_block_command(block, timestamp, verbose, as_json):
    if timestamp is not None and block is None:
        print('searching for block at timestamp:', timestamp)
        block = evm.get_block_of_timestamp(timestamp=timestamp, verbose=False)
        print('found block', block)
        print()

    if as_json:
        import rich
        import json
        block_data = await evm.async_get_block(block)
        rich.print_json(json.dumps(block_data))
    else:
        await evm.async_print_block_summary(block=block)

    await rpc.async_close_http_session()

