from __future__ import annotations

import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': ascii_command,
        'help': 'convert hex to ascii',
        'args': [
            {'name': 'data', 'help': 'hex data to convert'},
        ],
    }


def ascii_command(data: str) -> None:
    ascii = binary.hex_to_ascii(data)
    print(ascii)

