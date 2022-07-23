from __future__ import annotations

import asyncio

from ctc import spec
from . import erc20_metadata
from . import erc20_state


async def async_print_erc20_summary(
    erc20: spec.Address,
) -> None:
    import toolstr
    from ctc.cli import cli_run

    name_coroutine = erc20_metadata.async_get_erc20_name(
        erc20,
    )
    address_coroutine = erc20_metadata.async_get_erc20_address(
        erc20,
    )
    decimals_coroutine = erc20_metadata.async_get_erc20_decimals(erc20)
    symbol_coroutine = erc20_metadata.async_get_erc20_symbol(erc20)
    total_supply_coroutine = erc20_state.async_get_erc20_total_supply(erc20)

    name, address, decimals, symbol, total_supply = await asyncio.gather(
        name_coroutine,
        address_coroutine,
        decimals_coroutine,
        symbol_coroutine,
        total_supply_coroutine,
    )

    styles = cli_run.get_cli_styles()

    toolstr.print_text_box('ERC20 Summary', style=styles['title'])
    print('- address:', address)
    print('- name:', name)
    print('- symbol:', symbol)
    print('- decimals:', decimals)
    print('- total_supply:', toolstr.format(total_supply))
