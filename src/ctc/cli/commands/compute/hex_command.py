from __future__ import annotations

import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': hex_command,
        'help': 'convert text data to hex representation',
        'args': [
            {'name': 'text', 'help': 'ascii or other text data to convert'},
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'omit the "0x" prefix',
            },
        ],
        'examples': [
            'vitalik',
            'turducken',
        ],
    }


def hex_command(text: str, raw: bool) -> None:
    if raw:
        output = binary.ascii_to_raw_hex(text)
    else:
        output = binary.ascii_to_prefix_hex(text)
    print(output)
