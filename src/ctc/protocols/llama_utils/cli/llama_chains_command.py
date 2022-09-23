from __future__ import annotations

import toolcli

from .. import llama_tvls


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_chains_command,
        'help': 'output data about chains tracked by Defi Llama',
        'args': [
            {
                'name': '-n',
                'type': int,
                'default': 15,
                'help': 'number of chains to display',
            },
        ],
        'examples': [
            '',
            '-n 50',
        ],
    }


async def async_llama_chains_command(n: int = 15) -> None:
    await llama_tvls.async_print_chains_tvls(n=n)
