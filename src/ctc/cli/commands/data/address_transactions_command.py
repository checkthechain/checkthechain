from __future__ import annotations

import toolcli
import tooltable  # type: ignore

from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': address_transactions_command,
        'help': 'output all transactions from address',
        'args': [
            {'name': 'address', 'help': 'get transactions from this address'},
        ],
        'examples': ['0xd8da6bf26964af9d7eed9e03e53415d37aa96045'],
    }


async def address_transactions_command(address: spec.Address) -> None:

    print('fetching transactions from address', address)
    print()
    print('this may take some time...')
    print()

    transactions = await evm.async_get_transactions_from_address(address)

    rows = []
    for transaction in transactions:
        row = [
            transaction['nonce'],
            str(transaction['block_number']),
            transaction['hash'],
        ]
        rows.append(row)

    headers = ['#', 'block', 'transaction hash']
    tooltable.print_table(
        rows,
        headers=headers,
        compact=2,
    )

    await rpc.async_close_http_session()

