from __future__ import annotations

import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': hex_command,
        'help': 'convert ascii to hex',
        'args': [
            {'name': 'data', 'help': 'ascii data to convert'},
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


def hex_command(data: str, raw: bool) -> None:
    if raw:
        output = binary.ascii_to_raw_hex(data)
    else:
        output = binary.ascii_to_prefix_hex(data)
    print(output)
