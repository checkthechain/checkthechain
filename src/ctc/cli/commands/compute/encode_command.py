from __future__ import annotations

import ast
import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': encode_command,
        'help': """encode data

for simple datatypes, no quotes required

for nested datatypes, enclose in quotes and quote contained addresses""",
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
    if data.startswith('0x'):
        literal_data = data
    else:
        literal_data = ast.literal_eval(data)
    encoded = binary.encode_types(literal_data, type)
    as_hex = binary.convert(encoded, 'prefix_hex')
    print(as_hex)
