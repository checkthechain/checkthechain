from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': integer_command,
        'help': 'convert data to integer',
        'args': [
            {'name': 'data', 'help': 'hex data to convert to integer'},
        ],
        'examples': [
            '0xa00',
            '0x123456789abdef',
        ],
    }


def integer_command(data: str) -> None:
    as_int = evm.binary_convert(data, 'integer')
    print(as_int)
