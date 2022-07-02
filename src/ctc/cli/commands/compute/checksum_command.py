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
        'examples': [
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045',
        ],
    }


def checksum_command(address: spec.Address) -> None:
    print(evm.get_address_checksum(address))
