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
            '0x39aa39c021dfbae8fac545936693ac917d5e7563',
        ],
    }


async def async_llama_pool_command(pool: str) -> None:
    await llama_yields.async_summarize_pool_yield(pool)
