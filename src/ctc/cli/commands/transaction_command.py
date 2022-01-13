import asyncio

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': transaction_command,
        'args': [
            {'name': 'transaction'},
            {'name': '--sort'},
        ],
    }


def transaction_command(transaction, sort, **kwargs):

    asyncio.run(run(transaction=transaction, sort=sort))


async def run(transaction, sort):

    await evm.async_print_transaction_summary(
        transaction_hash=transaction, sort_logs_by=sort
    )

    from ctc.rpc.rpc_backends import rpc_http_async

    provider = rpc.get_provider()
    await rpc_http_async.async_close_session(provider=provider)

