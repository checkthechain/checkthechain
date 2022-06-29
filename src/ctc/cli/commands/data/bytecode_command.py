from __future__ import annotations

import toolcli

from ctc import evm
from ctc import rpc


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_bytecode_command,
        'help': 'get raw bytecode stored at address',
        'args': [
            {'name': 'address', 'help': 'address where bytecode is stored'},
        ],
        'examples': [
            '0x6b175474e89094c44da98b954eedeac495271d0f',
        ],
    }


async def async_bytecode_command(address: str) -> None:
    address = await evm.async_resolve_address(address)
    bytecode = await rpc.async_eth_get_code(address)
    print(bytecode)
