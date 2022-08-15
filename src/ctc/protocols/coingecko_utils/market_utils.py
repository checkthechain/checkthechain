from __future__ import annotations

import math
import os
import typing

if typing.TYPE_CHECKING:
    import aiohttp

import toolstr


url_template = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page={page}&sparkline=true&price_change_percentage=1h%2C24h%2C7d'
token_url_template = 'https://www.coingecko.com/en/coins/{name}'


async def async_get_market_data(
    n: int,
) -> typing.Sequence[typing.Mapping[typing.Any, typing.Any]]:
    import asyncio
    import aiohttp

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


def color_polarity(value: int | float | None) -> str:
    if value is None:
        return ''

    if value > 0:
        return '#8dc647'
    elif value < 0:
        return '#e15241'
    else:
        return 'gray'


def print_market_data(
    data: typing.Sequence[typing.Any],
    *,
    verbose: bool,
    include_links: bool = False,
    height: int | None = None,
    width: int | None = None,
    n_columns: int | None = None,
    gap: int | str | None = None,
) -> None:

    import toolcli

    if width is None:
        width = 8

    # create labels
    labels = ['token', 'price', 'Δ 1H', 'Δ 24H', 'Δ 7D', 'volume', 'mkt cap']
    if verbose:
        labels.append('7D chart')

    # create rows
    rows: list[typing.Sequence[typing.Any]] = []
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
            from toolstr.charts import braille_utils

            sparkline = braille_utils.create_braille_sparkline(
                data=item['sparkline_in_7d']['price'],
                # width=20,
                width=width,
                height=height,
            )

            row.append(sparkline)

        rows.append(row)

    if height is None:
        height = 1

    def get_row_color(r: int) -> str:
        if height is None:
            raise Exception('height not set')
        datum = data[int(r / height)]
        diff = (
            datum['sparkline_in_7d']['price'][-1]
            - datum['sparkline_in_7d']['price'][0]
        )
        return color_polarity(diff)

    # print table
    grey = '#BBBBBB'
    table_str = toolstr.print_multiline_table(
        rows,
        labels=labels,
        column_gap=1,
        # compact=True,
        add_row_index=True,
        separate_all_rows=False,
        max_table_width=toolcli.get_n_terminal_cols(),
        vertical_justify='center',
        border='#555555',
        label_style='#DDDDDD' + ' bold',
        column_styles={
            '': '#555555' + ' bold',
            'price': grey,
            'volume': grey,
            'mkt cap': grey,
            'Δ 1H': lambda context: 'bold ' + color_polarity(context['cell']),
            'Δ 24H': lambda context: 'bold ' + color_polarity(context['cell']),
            'Δ 7D': lambda context: 'bold ' + color_polarity(context['cell']),
            '7D chart': lambda context: 'bold ' + get_row_color(context['r']),
        },
        column_formats={
            'price': {'decimals': 2, 'trailing_zeros': True, 'prefix': '$'},
            'Δ 1H': {
                'scientific': False,
                'postfix': '%',
                'decimals': 2,
                'trailing_zeros': True,
            },
            'Δ 24H': {
                'scientific': False,
                'postfix': '%',
                'decimals': 2,
                'trailing_zeros': True,
            },
            'Δ 7D': {
                'scientific': False,
                'postfix': '%',
                'decimals': 2,
                'trailing_zeros': True,
            },
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
        return_str=True,
    )

    if n_columns is not None:
        if table_str is None:
            raise Exception('table_str not generated')
        columnized = toolstr.columnize(
            table_str,
            n_columns=n_columns,
            gap=gap,
            header_height=2,
        )
        toolstr.print(columnized)
    else:
        toolstr.print(table_str)
