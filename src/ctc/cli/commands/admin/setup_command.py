from __future__ import annotations

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': setup_command,
        'help': 'run ctc setup wizard',
        'examples': [''],
    }


def setup_command() -> None:
    from ctc.config import setup_utils

    setup_utils.setup_ctc()
