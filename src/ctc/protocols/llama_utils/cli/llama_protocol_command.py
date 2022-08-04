from __future__ import annotations

import toolcli

from .. import llama_tvls


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_protocol_command,
        'help': 'display information about specific protocol',
        'args': [
            {
                'name': 'protocol',
                'help': 'protocol to display information about',
            },
            {
                'name': ['-v', '--verbose'],
                'help': 'display additional infromation',
                'action': 'store_true',
            },
        ],
        'examples': [
            'Balancer',
            'Balancer --verbose',
        ],
    }


async def async_llama_protocol_command(protocol: str, verbose: bool) -> None:
    await llama_tvls.async_summarize_historical_protocol_tvl(
        protocol=protocol,
        verbose=verbose,
    )
