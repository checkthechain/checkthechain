from __future__ import annotations

import typing

import toolcli
import toolstr

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

        proxy_metadata = await evm.async_get_proxy_metadata(
            contract_address=contract_address,
            block=block,
        )
        proxy_address = proxy_metadata['address']
        if proxy_address is None:
            proxy_address = 'none'

        toolstr.print_text_box('Proxy Summary for ' + str(contract_address))
        rows: typing.Sequence[typing.Sequence[typing.Any]] = [
            ['contract_address', contract_address],
            ['block', block],
            ['uses EIP-897', proxy_metadata['proxy_type'] == 'eip897'],
            ['uses EIP-1967 Logic', proxy_metadata['proxy_type'] == 'eip1967-logic'],
            ['uses EIP-1967 Beacon', proxy_metadata['proxy_type'] == 'eip1967-beacon'],
            [
                'uses gnosis-proxy',
                proxy_metadata['proxy_type'] == 'gnosis_safe',
            ],
        ]
        toolstr.print_table(rows, column_justify=['right', 'left'], compact=2)
        print()
        print('proxy_address =', proxy_address)

    else:
        proxy_address = await evm.async_get_proxy_address(contract_address)
        if proxy_address is None:
            print('[no proxy address detected]')
        else:
            print(proxy_address)
