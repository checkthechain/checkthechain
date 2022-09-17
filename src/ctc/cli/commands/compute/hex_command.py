from __future__ import annotations

import toolcli

from ctc import evm


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
        output = evm.text_to_binary(text, 'raw_hex')
    else:
        output = evm.text_to_binary(text, 'prefix_hex')
    print(output)
