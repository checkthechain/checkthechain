from __future__ import annotations

import toolcli

from .. import llama_yields


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_pool_command,
        'help': 'output data about a pool tracked by Defi Llama',
        'args': [
            {
                'name': 'pool',
                'help': 'id of pool (obtain using --show-id on llama pools cmd)',
            },
        ],
        'examples': [
            '747c1d2a-c668-4682-b9f9-296708a3dd90',
        ],
    }


async def async_llama_pool_command(pool: str) -> None:
    await llama_yields.async_print_pool_yield_summary(pool)
