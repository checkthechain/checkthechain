from __future__ import annotations

import toolcli

from ctc import spec
from ctc.protocols import fei_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_pcv_deposits_command,
        'help': 'output summary of Fei PCV deposits',
        'args': [
            {'name': '--block', 'help': 'block number'},
        ],
        'examples': [
            '',
            '--block 14000000',
        ],
    }


async def async_pcv_deposits_command(
    block: spec.BlockNumberReference | None,
) -> None:
    await fei_utils.async_print_pcv_deposits(block=block)
