from __future__ import annotations

import toolcli
import toolstr

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_address_transactions_command,
        'help': 'output all transactions from address',
        'args': [
            {'name': 'address', 'help': 'get transactions from this address'},
        ],
        'examples': {
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045': {'long': True},
        },
    }


async def async_address_transactions_command(address: spec.Address) -> None:

    print('fetching transactions from address', address)
    print()
    print('this may take some time...')
    print()

    address = await evm.async_resolve_address(address)
    transactions = await evm.async_get_transactions_from_address(address)

    rows = []
    for transaction in transactions:
        row = [
            transaction['nonce'],
            str(transaction['block_number']),
            transaction['hash'],
        ]
        rows.append(row)

    labels = ['#', 'block', 'transaction hash']
    toolstr.print_table(
        rows,
        labels=labels,
        compact=True,
    )
