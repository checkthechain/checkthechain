from __future__ import annotations

import ast
import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': encode_command,
        'help': """encode data as EVM datatypes

for simple datatypes, no quotes required

for nested datatypes, enclose in quotes and quote contained addresses""",
        'args': [
            {
                'name': 'type',
                'help': 'datatype used for encoding',
                # 'dest': 'datatype',
            },
            {'name': 'data', 'help': 'data to be encoded'},
            {
                'name': '--packed',
                'help': 'encode like solidity\'s abi.encodePacked()',
                'action': 'store_true',
            },
        ],
        'examples': [
            'address 0x6b175474e89094c44da98b954eedeac495271d0f',
            '"(int64,int64,int64)" "[1,2,3]"',
        ],
    }


def encode_command(*, type: str, data: str, packed: bool) -> None:

    if ',' in type:
        if not type.startswith('('):
            type = '(' + type + ')'

    if data.startswith('0x'):
        literal_data = data
    else:
        try:
            literal_data = ast.literal_eval(data)
        except Exception:
            literal_data = ast.literal_eval('"' + data + '"')

    if packed:
        encoded = evm.abi_encode_packed(literal_data, type)
    else:
        encoded = evm.abi_encode(literal_data, type)

    as_hex = evm.binary_convert(encoded, 'prefix_hex')
    print(as_hex)
