from __future__ import annotations

import toolcli

from ctc.protocols import aave_v2_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_aave_addresses_command,
        'help': 'output aave-related addresses',
        'args': [
            {
                'name': ['--verbose', '-v'],
                'help': 'show additional addresses',
                'action': 'store_true',
            },
            {
                'name': '--block',
                'help': 'block to get addresses of',
            },
        ],
        'examples': [
            '',
            '--verbose',
            '--block 15000000',
        ],
    }


async def async_aave_addresses_command(
    verbose: bool,
    block: str | None,
) -> None:
    await aave_v2_utils.async_print_aave_addresses(
        verbose=verbose,
        block=block,
    )
