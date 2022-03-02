import asyncio
import sys
import math

import aiohttp
import toolcli
import toolstr
import tooltable

from rich.console import Console
from rich.theme import Theme


url_template = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page={page}&sparkline=true&price_change_percentage=1h%2C24h%2C7d'
token_url_template = 'https://www.coingecko.com/en/coins/{name}'


def get_command_spec():
    return {
        'f': async_cg_command,
        'args': [
            {'name': '-n'},
            {
                'name': '--verbose',
                'action': 'store_const',
                'const': True,
                'default': None,
            },
            {'name': '--include-links'},
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

    print_coingecko_data(data=data, verbose=verbose, include_links=include_links)


def print_coingecko_data(data, verbose, include_links):
    rows = []
    rows_colors = []

    headers = ['symbol', 'price', 'Δ 1H', 'Δ 24H', 'Δ 7D', 'volume', 'mkt cap']
    if verbose:
        headers.append('7d chart')

    for item in data:
        row = []
        row_colors = []
        row.append(item['symbol'].upper())

        price = toolstr.format_number(
            item['current_price'],
            decimals=2,
            trailing_zeros=True,
            prefix='$',
        )
        row.append(price)

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

        volume = toolstr.format(
            item['total_volume'],
            order_of_magnitude=True,
            prefix='$',
            trailing_zeros=True,
            decimals=1,
        )
        row.append(volume)

        market_cap = toolstr.format(
            item['market_cap'],
            order_of_magnitude=True,
            prefix='$',
            decimals=1,
            trailing_zeros=True,
        )
        row.append(market_cap)

        if verbose:
            from toolstr.charts import braille

            sparkline = braille.create_braille_sparkline(
                data=item['sparkline_in_7d']['price'],
                width=8,
            )
            row.append(sparkline)

        rows.append(row)

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

    console = Console(theme=Theme(inherit=False))
    all_lines = table['as_str'].split('\n')
    cell_lines = all_lines[2:]

    print(all_lines[0])
    print(all_lines[1])
    for l, (line, row_colors) in enumerate(zip(cell_lines, rows_colors)):
        cells = line.split('│')

        if include_links:
            name = data[l]['id']
            url = token_url_template.format(name=name)
            left_whitespace = len(cells[1]) - len(cells[1].lstrip())
            right_whitespace = len(cells[1]) - len(cells[1].rstrip())
            cells[1] = (
                '[link ' + url + ']' + cells[1].strip() + '[/link ' + url + ']'
            )
            cells[1] = ' ' * left_whitespace + cells[1] + ' ' * right_whitespace

        for rc, color in enumerate(row_colors):
            cells[2 + rc] = (
                '[' + color + ']' + cells[2 + rc] + '[/' + color + ']'
            )
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

