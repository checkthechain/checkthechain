from __future__ import annotations

import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': decode_command,
        'help': 'decode encoded data',
        'args': [
            {'name': 'type', 'help': 'type of data to decode'},
            {'name': 'data', 'help': 'data to decode'},
        ],
    }


def decode_command(type: str, data: str) -> None:
    decoded = binary.decode_types(binary.convert(data, 'binary'), type)
    print(decoded)
