from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_transaction_command,
        'help': 'summarize transaction and its receipt',
        'args': [
            {'name': 'transaction', 'help': 'hash of transaction'},
            {'name': '--sort', 'help': 'attribute to sort logs by'},
        ],
        'examples': [
            '0xe981fe5c78d11d935a1dc35c579969e65e2dd6bb05ad321ea9670f8b1e203eaf',
        ],
    }


async def async_transaction_command(transaction: str, sort: str) -> None:

    try:
        await evm.async_print_transaction_summary(
            transaction_hash=transaction, sort_logs_by=sort
        )
    except Exception:
        pass
