from __future__ import annotations

import toolcli

from .. import llama_tvls


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_command,
        'help': 'output data from Defi Llama api',
        'examples': [''],
    }


async def async_llama_command() -> None:
    await llama_tvls.async_print_historical_defi_tvl()
