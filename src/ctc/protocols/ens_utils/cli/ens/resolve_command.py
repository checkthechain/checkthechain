from __future__ import annotations

import toolcli

from ctc import binary
from ctc import spec
from ctc.protocols import ens_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_resolve_command,
        'help': 'resolve ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
            {'name': '--block', 'help': 'block number'},
        ]
    }


async def async_resolve_command(name: str, block: spec.BlockNumberReference) -> None:
    if block is not None:
        block = binary.standardize_block_number(block)
    address = await ens_utils.async_resolve_name(name, block=block)
    print(address)
