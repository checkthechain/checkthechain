from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': ascii_command,
        'help': 'convert hex to ascii',
        'args': [
            {'name': 'data', 'help': 'hex data to convert'},
        ],
        'examples': [
            '0x766974616c696b',
            '0x7475726475636b656e',
        ],
    }


def ascii_command(data: str) -> None:
    text = evm.binary_to_text(data)
    print(text)
