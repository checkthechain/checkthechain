from __future__ import annotations

import toolcli

from ctc import evm
from ctc import spec
from ctc.protocols import ens_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_owner_command,
        'help': 'output owner of ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
            {'name': '--block', 'help': 'block number'},
        ],
        'examples': [
            'vitalik.eth',
            'vitalik.eth --block 14000000',
        ],
    }


async def async_owner_command(
    name: str, block: spec.BlockNumberReference
) -> None:
    if block is not None:
        block = evm.standardize_block_number(block)
    owner = await ens_utils.async_get_owner(name, block=block)
    print(owner)
