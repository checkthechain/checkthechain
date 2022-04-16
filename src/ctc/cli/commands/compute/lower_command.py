from __future__ import annotations

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': lower_command,
        'help': 'convert to lower case',
        'args': [
            {'name': 'text', 'help': 'text to convert'},
        ],
    }


def lower_command(text: str) -> None:
    print(text.lower())

