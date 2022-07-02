from __future__ import annotations

import toolcli

from ctc.protocols import ens_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': hash_command,
        'help': 'output hash of ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
        ],
        'examples': [
            'vitalik.eth',
        ],
    }


def hash_command(name: str) -> None:
    print(ens_utils.hash_name(name))
