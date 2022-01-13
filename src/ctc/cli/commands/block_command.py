import asyncio

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': block_command,
        'args': [
            {'name': 'block', 'kwargs': {'nargs': '?'}},
            {'name': '--timestamp', 'kwargs': {'type': int}},
            {'name': '--verbose', 'kwargs': {'action': 'store_true'}},
        ],
    }


def block_command(block, timestamp, verbose=False, **kwargs):
    if timestamp is not None and block is None:
        print('searching for block at timestamp:', timestamp)
        block = evm.get_block_of_timestamp(timestamp=timestamp, verbose=False)
        print('found block', block)
        print()

    asyncio.run(run(block=block))


async def run(block):

    await evm.async_print_block_summary(block=block)

    from ctc.rpc.rpc_backends import rpc_http_async
    provider = rpc.get_provider()
    await rpc_http_async.async_close_session(provider=provider)

