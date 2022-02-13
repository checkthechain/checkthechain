from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_block_command,
        'args': [
            {'name': 'block', 'kwargs': {'nargs': '?'}},
            {'name': '--timestamp', 'kwargs': {'type': int}},
            {'name': '--verbose', 'kwargs': {'action': 'store_true'}},
        ],
    }


async def async_block_command(block, timestamp, verbose=False, **kwargs):
    if timestamp is not None and block is None:
        print('searching for block at timestamp:', timestamp)
        block = evm.get_block_of_timestamp(timestamp=timestamp, verbose=False)
        print('found block', block)
        print()

    await evm.async_print_block_summary(block=block)
    await rpc.async_close_http_session()

