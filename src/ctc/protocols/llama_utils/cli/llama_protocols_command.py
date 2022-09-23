from __future__ import annotations

import toolcli

from .. import llama_tvls


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_protocols_command,
        'help': 'output data about protocols tracked by Defi Llama',
        'args': [
            {
                'name': ['-v', '--verbose'],
                'help': 'show additional information',
                'action': 'store_true',
            },
            {
                'name': '--category',
                'help': 'filter protocols by category',
            },
            {
                'help': 'filter protocols by chain',
                'name': '--chain',
            },
            {
                'name': '-n',
                'help': 'number of protocols to display',
                'type': int,
                'default': 15,
            },
        ],
        'examples': [
            '',
            '--category Dexes',
            '--chain Tron',
        ],
    }


async def async_llama_protocols_command(
    *,
    verbose: bool = False,
    n: int = 50,
    category: str | None = None,
    chain: str | None = None,
) -> None:

    await llama_tvls.async_print_protocols_tvls(
        verbose=verbose,
        n=n,
        filter_category=category,
        filter_chain=chain,
    )
