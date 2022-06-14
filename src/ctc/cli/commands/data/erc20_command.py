from __future__ import annotations

import asyncio

import toolcli
import toolstr

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_erc20_command,
        'help': 'display information about ERC20',
        'args': [
            {
                'name': 'erc20',
            },
        ],
    }


async def async_erc20_command(erc20: str) -> None:
    name_coroutine = evm.async_get_erc20_name(
        erc20,
    )
    address_coroutine = evm.async_get_erc20_address(
        erc20,
    )
    decimals_coroutine = evm.async_get_erc20_decimals(erc20)
    symbol_coroutine = evm.async_get_erc20_symbol(erc20)
    total_supply_coroutine = evm.async_get_erc20_total_supply(erc20)

    name, address, decimals, symbol, total_supply = await asyncio.gather(
        name_coroutine,
        address_coroutine,
        decimals_coroutine,
        symbol_coroutine,
        total_supply_coroutine,
    )

    print('     address:', address)
    print('        name:', name)
    print('      symbol:', symbol)
    print('    decimals:', decimals)
    print('total_supply:', toolstr.format(total_supply))
