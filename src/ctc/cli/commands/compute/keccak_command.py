from __future__ import annotations

import typing

import toolcli

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': keccack_command,
        'help': 'compute keccak hash of data\n\nby default, data treated as hex if it starts with "0x", or treated as text otherwise',
        'args': [
            {'name': 'data', 'help': 'data to hash'},
            {
                'name': '--text',
                'action': 'store_true',
                'help': 'treat input data as text instead of hex',
            },
            {
                'name': '--hex',
                'action': 'store_true',
                'help': 'treat data as hex',
            },
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'omit "0x" prefix on output',
            },
        ],
        'examples': {
            '0x678acb67': 'take hash of hex data',
            'vitalik': 'take hash of text',
        },
    }


def keccack_command(*, data: str, text: bool, hex: bool, raw: bool) -> None:
    if text:
        hex = False
    elif hex:
        pass
    else:
        hex = data.startswith('0x')

    if hex:

        if typing.TYPE_CHECKING:
            casted = typing.cast(spec.GenericBinaryData, data)
        else:
            casted = data

        keccak = evm.keccak(casted, output_format='prefix_hex')
    else:
        keccak = evm.keccak_text(data)

    if raw:
        if not keccak.startswith('0x'):
            raise Exception('wrong format')
        keccak = keccak[2:]

    print(keccak)
