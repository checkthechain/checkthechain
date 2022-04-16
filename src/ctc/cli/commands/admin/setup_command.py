from __future__ import annotations

import toolcli

from ctc import config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': setup_command,
        'help': 'run ctc setup wizard',
    }


def setup_command() -> None:
    config.setup_ctc()

