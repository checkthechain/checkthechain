from __future__ import annotations

import asyncio
import math
import os
import sys
import typing

import aiohttp
import rich.console
import rich.theme
import toolstr


url_template = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page={page}&sparkline=true&price_change_percentage=1h%2C24h%2C7d'
token_url_template = 'https://www.coingecko.com/en/coins/{name}'


async def async_get_market_data(
    n: int,
) -> typing.Sequence[typing.Mapping[typing.Any, typing.Any]]:
    n_per_page = 100
    n_pages = math.ceil(n / n_per_page)

    async with aiohttp.ClientSession() as session:
        coroutines = [async_get_page(session, p) for p in range(n_pages)]
        pages = await asyncio.gather(*coroutines)

    items = [item for page in pages for item in page]

    return items[:n]


async def async_get_page(
    session: aiohttp.ClientSession, p: int
) -> typing.List[typing.Any]:
    url = url_template.format(page=p + 1)
    async with session.get(url) as response:
        page = await response.json()
        if not isinstance(page, list):
            raise Exception('bad page format')
        return page


def print_market_data(
    data: typing.Sequence[typing.Any],
    verbose: bool,
    include_links: bool,
) -> None:

    # create headers
    headers = ['symbol', 'price', 'Δ 1H', 'Δ 24H', 'Δ 7D', 'volume', 'mkt cap']
    if verbose:
        headers.append('7D chart')

    # create rows
    rows = []
    for item in data:

        row = []
        row.append(item['symbol'].upper())
        row.append(item['current_price'])

        # add price change cells
        for key in [
            'price_change_percentage_1h_in_currency',
            'price_change_percentage_24h_in_currency',
            'price_change_percentage_7d_in_currency',
        ]:
            change = item[key]
            row.append(change)

        row.append(item['total_volume'])
        row.append(item['market_cap'])

        # add sparkline
        if verbose:
            from toolstr.charts import braille

            sparkline = braille.create_braille_sparkline(
                data=item['sparkline_in_7d']['price'],
                width=8,
            )
            row.append(sparkline)

        rows.append(row)

    def color_polarity(value: int | float) -> str:
        if value > 0:
            return '#4eaf0a'
        elif value < 0:
            return '#e15241'
        else:
            return 'gray'

    # print table
    toolstr.print_table(
        rows,
        headers=headers,
        add_row_index=True,
        # max_table_width=os.get_terminal_size().columns,
        column_style={
            'Δ 1H': lambda context: 'bold ' + color_polarity(context['cell']),
            'Δ 24H': lambda context: 'bold ' + color_polarity(context['cell']),
            'Δ 7D': lambda context: 'bold ' + color_polarity(context['cell']),
            '7D chart': lambda context: 'bold '
            + color_polarity(context['row'][context['labels'].index('Δ 7D')]),
        },
        column_format={
            'price': {'decimals': 2, 'trailing_zeros': True, 'prefix': '$'},
            'Δ 1H': {'postfix': '%', 'decimals': 2, 'trailing_zeros': True},
            'Δ 24H': {'postfix': '%', 'decimals': 2, 'trailing_zeros': True},
            'Δ 7D': {'postfix': '%', 'decimals': 2, 'trailing_zeros': True},
            'volume': {
                'decimals': 1,
                'trailing_zeros': True,
                'prefix': '$',
                'order_of_magnitude': True,
            },
            'mkt cap': {
                'decimals': 1,
                'trailing_zeros': True,
                'prefix': '$',
                'order_of_magnitude': True,
            },
        },
    )
