from __future__ import annotations

import toolcli

from ctc.protocols import fei_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_pcv_assets_command,
        'help': 'output summary of Fei PCV assets',
        'args': [
            {'name': '--block', 'help': 'block number'},
        ],
        'examples': [
            '',
            '--block 14000000',
        ],
    }


async def async_pcv_assets_command(block: str) -> None:
    await fei_utils.async_print_pcv_assets(block=block)
