from __future__ import annotations

import toolcli
import toolstr

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
                'name': ['-t', '--time'],
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
            'CRV -t 100d',
            'ETH / BTC',
            'LINK / ETH -t 24h',
            '--update',
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

    if update:
        await coingecko_utils.async_get_token_list(use_db=False, update=True)
        return

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

        terminal_rows = toolcli.get_n_terminal_rows()
        terminal_columns = toolcli.get_n_terminal_cols()
        if n is None:
            if terminal_columns > 172:
                n_columns = 2
                gap = 4
                n = (terminal_rows - 4) * 2

            else:
                n_columns = None
                gap = None

                n = terminal_rows - 4
                n = int(n / height)

        else:
            n = int(n)

            if n > terminal_rows - 4 and terminal_columns > 172:
                n_columns = 2
                gap = 4

        data = await coingecko_utils.async_get_market_data(n)

        if verbose is None:
            verbose = toolcli.get_n_terminal_cols() >= 96

        coingecko_utils.print_market_data(
            data=data,
            verbose=verbose,
            height=height,
            width=width,
            n_columns=n_columns,
            gap=gap,
        )

        note = 'coingecko data @ ' + str(data[0]['last_updated'])
        toolstr.print(note, style='#555555')

    elif len(tokens) == 3 and tokens[1] == '/':
        await coingecko_utils.async_print_coin_quotient_summary(
            tokens[0],
            tokens[2],
            days=days,
        )

    elif len(tokens) == 1:

        await coingecko_utils.async_print_token_data_summary(
            query=tokens[0],
            verbose=verbose,
            update=update,
            days=days,
        )

    else:
        raise Exception('could not parse inputs, use --help for details')
