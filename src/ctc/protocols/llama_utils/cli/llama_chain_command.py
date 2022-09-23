from __future__ import annotations

import toolcli

from .. import llama_tvls


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_chain_command,
        'help': 'output data about a chain tracked by Defi Llama',
        'args': [
            {
                'name': 'chain',
                'help': 'chain to describe',
            },
        ],
        'examples': [
            'Tezos',
        ],
    }


async def async_llama_chain_command(chain: str) -> None:
    await llama_tvls.async_print_historical_chain_tvl(chain)
