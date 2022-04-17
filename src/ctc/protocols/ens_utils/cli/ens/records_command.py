from __future__ import annotations

import toolcli

from ctc.protocols import ens_utils
from ctc import rpc


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_records_command,
        'help': 'output text records of ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
        ],
    }


async def async_records_command(name: str) -> None:
    text_records = await ens_utils.async_get_text_records(name=name)

    for key, value in sorted(text_records.items()):
        print('-', key + ':', value)

    await rpc.async_close_http_session()

