import asyncio

from ctc import rpc
from ctc.protocols import chainlink_utils


def get_command_spec():
    return {
        'f': chainlink_command,
        'options': [
            {'name': 'feed'},
        ]
    }


def chainlink_command(feed, **kwargs):
    asyncio.run(run(feed))


async def run(feed):
    await chainlink_utils.async_summarize_feed(feed=feed)

    from ctc.rpc.rpc_backends import rpc_http_async

    provider = rpc.get_provider()
    await rpc_http_async.async_close_session(provider=provider)

