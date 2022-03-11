import asyncio
import sys
import math

import aiohttp
import rich.console
import rich.theme
import toolcli
import toolstr
import tooltable  # type: ignore


url_template = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page={page}&sparkline=true&price_change_percentage=1h%2C24h%2C7d'
token_url_template = 'https://www.coingecko.com/en/coins/{name}'


def get_command_spec():
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
    }


async def async_get_coingecko_data(n):
    n_per_page = 100
    n_pages = math.ceil(n / n_per_page)

    async with aiohttp.ClientSession() as session:
        coroutines = [async_get_page(session, p) for p in range(n_pages)]
        pages = await asyncio.gather(*coroutines)

    items = [item for page in pages for item in page]

    return items[:n]


async def async_get_page(session, p):
    url = url_template.format(page=p + 1)
    async with session.get(url) as response:
        return await response.json()


async def async_cg_command(n, verbose, include_links):

    if n is None:
        n = toolcli.get_n_terminal_rows() - 3
    else:
        n = int(n)

    data = await async_get_coingecko_data(n)

    if verbose is None:
        verbose = toolcli.get_n_terminal_cols() >= 96

    print_coingecko_data(
        data=data, verbose=verbose, include_links=include_links
    )


def print_coingecko_data(data, verbose, include_links):

    # create headers
    headers = ['symbol', 'price', 'Δ 1H', 'Δ 24H', 'Δ 7D', 'volume', 'mkt cap']
    if verbose:
        headers.append('7d chart')

    # create rows
    rows = []
    rows_colors = []
    for item in data:

        row = []
        row_colors = []

        # add symbol cell
        row.append(item['symbol'].upper())

        # add price cell
        price = toolstr.format_number(
            item['current_price'],
            decimals=2,
            trailing_zeros=True,
            prefix='$',
        )
        row.append(price)

        # add price change cells
        for key in [
            'price_change_percentage_1h_in_currency',
            'price_change_percentage_24h_in_currency',
            'price_change_percentage_7d_in_currency',
        ]:
            change = toolstr.format_number(
                item[key],
                decimals=2,
                signed=True,
                postfix='%',
                trailing_zeros=True,
            )
            if item[key] < 0:
                color = '#e15241'
            elif item[key] > 0:
                color = '#4eaf0a'
            else:
                color = 'black'
            row_colors.append(color)
            row.append(change)
        rows_colors.append(row_colors)

        # add volume cell
        volume = toolstr.format(
            item['total_volume'],
            order_of_magnitude=True,
            prefix='$',
            trailing_zeros=True,
            decimals=1,
        )
        row.append(volume)

        # add market cap
        market_cap = toolstr.format(
            item['market_cap'],
            order_of_magnitude=True,
            prefix='$',
            decimals=1,
            trailing_zeros=True,
        )
        row.append(market_cap)

        # add sparkline
        if verbose:
            from toolstr.charts import braille

            sparkline = braille.create_braille_sparkline(
                data=item['sparkline_in_7d']['price'],
                width=8,
            )
            row.append(sparkline)

        rows.append(row)

    # render table without sending to stdout
    old_stdout = sys.stdout
    sys.stdout = None
    table = tooltable.print_table(
        rows,
        headers=headers,
        justify='right',
        row_index=True,
        trim_to_terminal=True,
    )
    sys.stdout = old_stdout

    # TODO: incorporate colors directly into table rendering function
    # - the current solution is very hacky

    # colorize table and print
    all_lines = table['as_str'].split('\n')
    cell_lines = all_lines[2:]
    console = rich.console.Console(theme=rich.theme.Theme(inherit=False))
    print(all_lines[0])
    print(all_lines[1])
    for rank, (line, row_colors) in enumerate(zip(cell_lines, rows_colors)):

        # split row into cells
        cells = line.split('│')

        # create link around token symbol
        if include_links:
            name = data[rank]['id']
            url = token_url_template.format(name=name)
            left_whitespace = len(cells[1]) - len(cells[1].lstrip())
            right_whitespace = len(cells[1]) - len(cells[1].rstrip())
            cells[1] = (
                '[link ' + url + ']' + cells[1].strip() + '[/link ' + url + ']'
            )
            cells[1] = ' ' * left_whitespace + cells[1] + ' ' * right_whitespace

        # colorize price changes
        for rc, color in enumerate(row_colors):
            cells[3 + rc] = (
                '[' + color + ']' + cells[3 + rc] + '[/' + color + ']'
            )

        # colorize sparklink
        if verbose:
            cells[-1] = (
                '['
                + row_colors[-1]
                + ' bold]'
                + cells[-1]
                + '[/'
                + row_colors[-1]
                + ' bold]'
            )

        color_line = '│'.join(cells)
        console.print(color_line)

