from __future__ import annotations

import toolcli

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': checksum_command,
        'help': 'compute checksum of address',
        'args': [
            {'name': 'address', 'help': 'address to get checksum of'},
        ],
    }


def checksum_command(address: spec.Address) -> None:
    print(evm.get_address_checksum(address))

