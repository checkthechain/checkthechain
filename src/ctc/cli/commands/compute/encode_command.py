from __future__ import annotations

import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': encode_command,
        'help': 'encode data',
        'args': [
            {
                'name': 'type',
                'help': 'datatype used for encoding',
                # 'dest': 'datatype',
            },
            {'name': 'data', 'help': 'data to be encoded'},
        ],
    }


def encode_command(type: str, data: str) -> None:
    encoded = binary.encode_types(data, type)
    as_hex = binary.convert(encoded, 'prefix_hex')
    print(as_hex)
