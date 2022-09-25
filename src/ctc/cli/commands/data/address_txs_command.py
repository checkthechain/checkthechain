from __future__ import annotations

import typing

import toolcli
import toolstr
import tooltime

from ctc import cli
from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_address_transactions_command,
        'help': 'output all transactions from address',
        'args': [
            {'name': 'address', 'help': 'get transactions from this address'},
            {
                'name': ['-v', '--verbose'],
                'help': 'display additional information',
                'action': 'store_true',
            },
        ],
        'examples': {
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045': {'long': True},
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 -v': {'long': True},
        },
    }


async def async_address_transactions_command(
    address: spec.Address,
    verbose: bool,
) -> None:

    styles = cli.get_cli_styles()
    toolstr.print(
        'fetching transactions from address',
        toolstr.add_style(address, styles['metavar']),
    )
    print()
    print('this may take some time...')
    print()

    # get row limit
    if verbose:
        limit_rows = None
    else:
        limit_rows = toolcli.get_n_terminal_rows() - 8

    address = await evm.async_resolve_address(address)
    transactions = await evm.async_get_transactions_from_address(address)

    # get block numbers
    if verbose:
        block_numbers = [
            transaction['block_number'] for transaction in transactions
        ]
        block_timestamps = await evm.async_get_block_timestamps(block_numbers)

    rows = []
    for t, transaction in enumerate(transactions):

        row: list[typing.Any] = [transaction['nonce']]
        row.append(str(transaction['block_number']))
        if verbose:
            timestamp = block_timestamps[t]
            row.append(tooltime.timestamp_to_iso_pretty(timestamp))
        row.append(transaction['hash'])

        rows.append(row)

    if verbose:
        labels = ['#', 'block', 'timestamp', 'transaction hash']
    else:
        labels = ['#', 'block', 'transaction hash']

    toolstr.print_table(
        rows,
        labels=labels,
        compact=2,
        limit_rows=limit_rows,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            '#': styles['option'],
            'block': styles['description'],
            'timestamp': styles['description'],
            'transaction hash': styles['metavar'],
        },
    )
