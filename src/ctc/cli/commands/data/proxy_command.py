from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_proxy_command,
        'help': 'print proxy information about contract',
        'args': [
            {'name': 'contract_address', 'help': 'address to get proxy of'},
            {
                'name': ['--verbose', '-v'],
                'help': 'print additional information',
                'action': 'store_true',
            },
            {'name': '--block', 'help': 'block to query', 'default': 'latest'},
        ],
        'examples': [
            '0xee6a57ec80ea46401049e92587e52f5ec1c24785',  # EIP1967
        ],
    }


async def async_proxy_command(
    *,
    contract_address: spec.Address,
    verbose: bool,
    block: spec.BlockNumberReference,
) -> None:

    contract_address = await evm.async_resolve_address(
        contract_address,
        block=block,
    )

    if verbose:

        styles = cli.get_cli_styles()

        proxy_metadata = await evm.async_get_proxy_metadata(
            contract_address=contract_address,
            block=block,
        )

        if proxy_metadata['implementation'] is None:
            toolstr.print(
                'no proxy detected for '
                + toolstr.add_style(contract_address, styles['metavar']),
            )
            return

        toolstr.print_text_box(
            'Proxy Summary for ' + str(contract_address),
            style=styles['title'],
        )
        rows: typing.Sequence[typing.Sequence[typing.Any]] = [
            ['proxy', toolstr.add_style(contract_address, styles['metavar'])],
            [
                'implementation',
                toolstr.add_style(
                    proxy_metadata['implementation'], styles['metavar']
                ),
            ],
            ['block', block],
            ['proxy_type', proxy_metadata['proxy_type']],
        ]
        toolstr.print_table(
            rows,
            column_justify=['right', 'left'],
            compact=2,
            border=styles['comment'],
            column_styles=[styles['option'], styles['description'] + ' bold'],
            indent=4,
        )

    else:
        proxy_address = await evm.async_get_proxy_implementation(
            contract_address
        )
        if proxy_address is None:
            print('[no proxy address detected]')
        else:
            print(proxy_address)
