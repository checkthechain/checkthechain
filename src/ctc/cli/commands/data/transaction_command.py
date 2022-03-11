import asyncio

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': transaction_command,
        'help': 'summarize transaction',
        'args': [
            {'name': 'transaction', 'help': 'hash of transaction'},
            {'name': '--sort', 'help': 'attribute to sort logs by'},
        ],
    }


def transaction_command(transaction, sort, **kwargs):

    asyncio.run(run(transaction=transaction, sort=sort))


async def run(transaction, sort):

    await evm.async_print_transaction_summary(
        transaction_hash=transaction, sort_logs_by=sort
    )

    await rpc.async_close_http_session()

