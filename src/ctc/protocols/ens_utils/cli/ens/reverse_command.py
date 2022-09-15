from __future__ import annotations

import toolcli

from ctc import evm
from ctc import spec
from ctc.protocols import ens_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_reverse_command,
        'help': 'reverse ENS lookup address',
        'args': [
            {'name': 'address', 'help': 'address of reverse lookup'},
            {'name': '--block', 'help': 'block number'},
        ],
        'examples': [
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 --block 14000000',
        ],
    }


async def async_reverse_command(
    address: spec.Address,
    block: spec.BlockNumberReference,
) -> None:
    if block is not None:
        block = evm.standardize_block_number(block)
    name = await ens_utils.async_reverse_lookup(address, block=block)
    print(name)
