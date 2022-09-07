from __future__ import annotations

import toolcli

from ctc import cli
from ctc.protocols import ens_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_records_command,
        'help': 'output text records of ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
        ],
        'examples': [
            'vitalik.eth',
        ],
    }


async def async_records_command(name: str) -> None:
    text_records = await ens_utils.async_get_text_records(name=name)

    for key, value in sorted(text_records.items()):
        cli.print_bullet(key=key, value=value)
