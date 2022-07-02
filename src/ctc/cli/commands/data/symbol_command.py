from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_symbol_command,
        'help': 'convert ERC20 address to symbol, or symbol to address',
        'args': [
            {'name': 'query', 'help': 'ERC20 address or symbol'},
        ],
        'examples': [
            'DAI',
        ],
    }


async def async_symbol_command(query: str) -> None:
    if evm.is_address_str(query):
        symbol = await evm.async_get_erc20_symbol(query)
        print(symbol)
    else:
        try:
            address = await evm.async_get_erc20_address(query)
            print(address)
        except Exception:
            print(
                'could not find address for token with symbol "'
                + str(query)
                + '"'
            )
