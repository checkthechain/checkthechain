from __future__ import annotations

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': lower_command,
        'help': 'convert string to lower case',
        'args': [
            {'name': 'text', 'help': 'text to convert'},
        ],
        'examples': [
            '0x956F47F50A910163D8BF957Cf5846D573E7f87CA',
        ],
    }


def lower_command(text: str) -> None:
    print(text.lower())
