from __future__ import annotations

import toolcli
import toolstr

from ctc.cli import cli_run
from ctc.protocols import coingecko_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_cg_command,
        'help': 'output coingecko market data',
        'args': [
            {
                'name': 'tokens',
                'help': 'token to display information of',
                'nargs': '*',
            },
            {
                'name': '--time',
                'help': 'time of chart (e.g. 7d, 1y, max)',
                'dest': 'timelength',
            },
            {'name': '-n', 'help': 'number of entries to include in output'},
            {
                'name': ['--verbose', '-v'],
                'action': 'store_const',
                'const': True,
                'default': None,
                'help': 'include extra data',
            },
            {'name': '--height', 'help': 'height, number of rows per asset'},
            {'name': '--width', 'help': 'width of sparklines'},
            {
                'name': '--update',
                'help': 'update stored coingecko token db',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            'CRV',
            '--update',
            'ETH / BTC',
            'ETH / LINK',
        ],
    }


async def async_cg_command(
    *,
    tokens: str,
    n: int,
    verbose: bool,
    height: int | None,
    width: str | int | None,
    update: bool,
    timelength: str | None,
) -> None:

    if height is None:
        height = 1
    height = int(height)

    if isinstance(width, str):
        width = int(width)

    if timelength is not None:
        if timelength == 'max':
            days = None
        else:
            import tooltime

            days = round(tooltime.timelength_to_seconds(timelength) / 86400)
    else:
        days = 30

    if len(tokens) == 0:

        if n is None:
            n = toolcli.get_n_terminal_rows() - 4
            n = int(n / height)
        else:
            n = int(n)

        data = await coingecko_utils.async_get_market_data(n)

        if verbose is None:
            verbose = toolcli.get_n_terminal_cols() >= 96

        styles = cli_run.get_cli_styles()
        note = 'coingecko data @ ' + str(data[0]['last_updated'])
        toolstr.print(note, style=styles['comment'])

        coingecko_utils.print_market_data(
            data=data,
            verbose=verbose,
            height=height,
            width=width,
        )

    elif len(tokens) == 3 and tokens[1] == '/':
        await coingecko_utils.async_summarize_coin_quotient(
            tokens[0],
            tokens[2],
            days=days,
        )

    elif len(tokens) == 1:

        await coingecko_utils.async_summarize_token_data(
            query=tokens[0],
            verbose=verbose,
            update=update,
            days=days,
        )

    else:
        raise Exception('could not parse inputs, use --help for details')
