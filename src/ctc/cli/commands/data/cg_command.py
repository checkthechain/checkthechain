from __future__ import annotations

import toolcli

from ctc.protocols import coingecko_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_cg_command,
        'help': 'output coingecko market data',
        'args': [
            {'name': '-n', 'help': 'number of entries to include in output'},
            {
                'name': '--verbose',
                'action': 'store_const',
                'const': True,
                'default': None,
                'help': 'include extra data',
            },
            {'name': '--include-links', 'help': 'include links in output'},
        ],
        'examples': [
            '',
            '-n 100',
        ],
    }


async def async_cg_command(n: int, verbose: bool, include_links: bool) -> None:

    if n is None:
        n = toolcli.get_n_terminal_rows() - 3
    else:
        n = int(n)

    data = await coingecko_utils.async_get_market_data(n)

    if verbose is None:
        verbose = toolcli.get_n_terminal_cols() >= 96

    coingecko_utils.print_market_data(
        data=data,
        verbose=verbose,
        include_links=include_links,
    )
