from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_transaction_command,
        'help': 'display transaction data, receipt, call data, & logs',
        'args': [
            {'name': 'transaction', 'help': 'hash of transaction'},
            {'name': '--sort', 'help': 'attribute to sort logs by'},
            {
                'name': '--json',
                'help': 'output raw JSON of tx',
                'action': 'store_true',
                'dest': 'as_json',
            },
        ],
        'examples': [
            '0xe981fe5c78d11d935a1dc35c579969e65e2dd6bb05ad321ea9670f8b1e203eaf',
        ],
    }


async def async_transaction_command(
    *, transaction: str, sort: str, as_json: bool
) -> None:

    if as_json:
        import json

        transaction_data = await evm.async_get_transaction(transaction)
        print(json.dumps(transaction_data, sort_keys=True, indent=4))

    else:
        await evm.async_print_transaction_summary(
            transaction_hash=transaction, sort_logs_by=sort
        )
