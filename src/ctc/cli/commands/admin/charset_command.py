from __future__ import annotations

import toolcli
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': charset_command,
        'help': 'change character sets used for plotting',
        'args': [
            {
                'name': 'charset',
                'help': 'charset to switch to',
                'nargs': '?',
            },
            {
                'name': ['-v', '--verbose'],
                'help': 'display available charsets',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            'braille',
            'quadrants',
            '-v',
        ]
    }


def charset_command(charset: str | None, verbose: bool) -> None:

    if verbose:
        cli_utils.preview_available_charsets()
    elif charset is None:
        cli_utils.print_current_charset()
    else:
        cli_utils.set_charset(charset)
