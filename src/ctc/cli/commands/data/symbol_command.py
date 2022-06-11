from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_symbol_command,
        'help': 'output address of ERC20 symbol',
        'args': [
            {'name': 'symbol', 'help': 'ERC20 symbol'},
        ],
    }


async def async_symbol_command(symbol: str) -> None:
    address = await evm.async_get_erc20_address(symbol)
    print(address)
