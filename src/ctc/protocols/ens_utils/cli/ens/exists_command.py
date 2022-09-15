from __future__ import annotations

import toolcli

from ctc.protocols import ens_utils
from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_exists_command,
        'help': 'output whether ENS name exists',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
            {'name': '--block', 'help': 'block number'},
        ],
        'examples': [
            'vitalik.eth',
            'vitalik.eth --block 14000000',
            'fake-vitalik.eth',
        ],
    }


async def async_exists_command(
    name: str, block: spec.BlockNumberReference
) -> None:

    if block is not None:
        block = evm.standardize_block_number(block)
    exists = await ens_utils.async_record_exists(name, block=block)

    print(exists)
