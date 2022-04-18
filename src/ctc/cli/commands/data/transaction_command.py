from __future__ import annotations

import asyncio

import toolcli

from ctc import evm
from ctc import rpc


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': transaction_command,
        'help': 'summarize transaction',
        'args': [
            {'name': 'transaction', 'help': 'hash of transaction'},
            {'name': '--sort', 'help': 'attribute to sort logs by'},
        ],
    }


def transaction_command(transaction: str, sort: str) -> None:

    asyncio.run(run(transaction=transaction, sort=sort))


async def run(transaction: str, sort: str) -> None:

    await evm.async_print_transaction_summary(
        transaction_hash=transaction, sort_logs_by=sort
    )

    await rpc.async_close_http_session()

