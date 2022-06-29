from __future__ import annotations

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_setup_command,
        'help': 'run ctc setup wizard',
        'examples': {
            '': {'skip': True},
        },
    }


async def async_setup_command() -> None:
    from ctc.config import setup_utils

    await setup_utils.async_setup_ctc()
