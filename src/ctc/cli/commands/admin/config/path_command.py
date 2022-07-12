from __future__ import annotations

import toolcli

from ctc import config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': path_command,
        'help': 'print config path',
        'examples': [''],
        'hidden': True,
    }


def path_command() -> None:
    print(config.get_config_path(raise_if_dne=False))
