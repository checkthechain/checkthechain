from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': decode_command,
        'help': """decode encoded EVM datatypes

for simple datatypes, no quotes required

for nested datatypes, enclose in quotes and quote contained addresses""",
        'args': [
            {'name': 'type', 'help': 'type of data to decode'},
            {'name': 'data', 'help': 'data to decode'},
        ],
        'examples': [
            'address 0x0000000000000000000000006b175474e89094c44da98b954eedeac495271d0f',
            '"(int64,int64,int64)" 0x000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003',
        ],
    }


def decode_command(type: str, data: str) -> None:
    decoded = evm.abi_decode(evm.binary_convert(data, 'binary'), type)
    print(decoded)
