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
                'name': ['--verbose', '-v'],
                'help': 'display additional information',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0x245cc372c84b3645bf0ffe6538620b04a217988b',
            '0x245cc372c84b3645bf0ffe6538620b04a217988b --verbose',
        ],
    }


async def async_gnosis_command(address: str, verbose: bool) -> None:
    await gnosis_safe_data.async_print_safe_summary(address, verbose=verbose)
