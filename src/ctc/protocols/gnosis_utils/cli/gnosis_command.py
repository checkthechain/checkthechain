from __future__ import annotations

import toolcli

from .. import gnosis_safe_data


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_gnosis_command,
        'help': 'print information about a gnosis safe',
        'args': [
            {'name': 'address', 'help': 'address of gnosis safe'},
            {
                'name': '--verbose',
                'help': 'display additional information',
                'action': 'store_true',
            },
        ],
    }


async def async_gnosis_command(address: str, verbose: bool) -> None:
    await gnosis_safe_data.async_print_safe_summary(address, verbose=verbose)
