from __future__ import annotations

import typing

from ctc import spec
from . import erc20_metadata
from . import erc20_state


async def async_print_erc20_summary(
    erc20: spec.Address,
    include_address: bool = True,
) -> None:
    """print ERC20 summary"""

    import asyncio
    import toolstr
    from ctc import cli

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

    styles = cli.get_cli_styles()

    toolstr.print_text_box('ERC20 Summary for ' + symbol, style=styles['title'])

    rows: typing.MutableSequence[typing.Tuple[str, typing.Any]] = []
    rows.append(('name', name))
    rows.append(('symbol', symbol))
    rows.append(('decimals', decimals))
    rows.append(
        (
            'total_supply',
            toolstr.format(
                total_supply, order_of_magnitude=True, trailing_zeros=True
            ),
        )
    )
    print()
    toolstr.print_table(
        rows,
        # indent=4,
        border=styles['comment'],
        column_styles=[styles['option'], styles['description']],
    )

    if include_address:
        print()
        toolstr.print(address, style=styles['metavar'])
