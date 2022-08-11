from __future__ import annotations

import toolcli

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_address_command,
        'help': """summarize address

for contracts, will display ABI""",
        'args': [
            {'name': 'address', 'help': 'address to get summary of'},
            {
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'emit extra output',
            },
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'emit abi in raw json',
            },
            {
                'name': '--network',
                'metavar': 'NAME_OR_ID',
                'help': 'network name or id to scan address of',
            },
        ],
        'examples': ['0x956f47f50a910163d8bf957cf5846d573e7f87ca'],
    }


async def async_address_command(
    *, address: spec.Address, verbose: bool | int, network: str, raw: bool
) -> None:

    max_width = toolcli.get_n_terminal_cols()

    address = await evm.async_resolve_address(address)

    if verbose:
        verbose = 2
    await evm.async_print_address_summary(
        address=address,
        verbose=verbose,
        max_width=max_width,
        raw=raw,
        provider={'network': network},
    )
