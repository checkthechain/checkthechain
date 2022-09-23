from __future__ import annotations

import toolstr

from ctc import cli
from . import llama_requests


#
# # comparisons
#


async def async_print_protocols_tvls(
    *,
    verbose: bool = False,
    n: int = 50,
    filter_category: str | None = None,
    filter_chain: str | None = None,
) -> None:

    styles = cli.get_cli_styles()

    data = await llama_requests.async_get_protocols_tvls(
        category=filter_category,
        chain=filter_chain,
    )

    keys = [
        'name',
        'category',
        'chain',
        'tvl',
    ]

    if verbose:
        keys.append('slug')

    rows = []
    for datum in data[:n]:
        name = ' '.join(datum['name'].split(' ')[:2])
        row = [name, datum['category'], datum['chain'], datum['tvl']]
        if verbose:
            row.append(datum['slug'])
        rows.append(row)
    if n < len(data):
        rows.append(['...'] * len(keys))

    toolstr.print_text_box('TVL by Protocol', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        labels=keys,
        column_formats={
            'tvl': {
                'order_of_magnitude': True,
                'decimals': 2,
                'trailing_zeros': True,
                'prefix': '$',
            },
        },
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'tvl': styles['description'],
        },
    )


async def async_print_chains_tvls(n: int = 50) -> None:

    styles = cli.get_cli_styles()

    data = await llama_requests.async_get_chains_tvls()

    keys = [
        'name',
        'tvl',
    ]

    data = sorted(data, key=lambda datum: float(datum['tvl']), reverse=True)

    rows = []
    for datum in data[:n]:
        name = ' '.join(datum['name'].split(' ')[:2])
        row = [name, datum['tvl']]
        rows.append(row)

    if len(data) > n:
        rows.append(['...'] * len(keys))

    toolstr.print_text_box('TVL by Chain', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        labels=keys,
        column_formats={
            'tvl': {
                'order_of_magnitude': True,
                'decimals': 2,
                'trailing_zeros': True,
                'prefix': '$',
            },
        },
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'tvl': styles['description'],
        },
    )


#
# # historical charting
#


async def async_print_historical_defi_tvl() -> None:

    styles = cli.get_cli_styles()

    data = await llama_requests.async_get_historical_defi_tvl()

    plot = toolstr.render_line_plot(
        xvals=data['timestamp'],
        yvals=data['tvl'],
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
        yaxis_kwargs={'tick_label_format': {'prefix': '$'}},
    )

    toolstr.print_text_box('Historical Defi TVL', style=styles['title'])
    print()
    toolstr.print(plot)


async def async_print_historical_chain_tvl(chain: str) -> None:

    styles = cli.get_cli_styles()

    data = await llama_requests.async_get_historical_chain_tvl(chain)

    plot = toolstr.render_line_plot(
        xvals=data['timestamp'],
        yvals=data['tvl'],
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
        yaxis_kwargs={'tick_label_format': {'prefix': '$'}},
    )

    toolstr.print_text_box(
        'Historical ' + chain + ' TVL', style=styles['title']
    )
    print()
    toolstr.print(plot, indent=4)


async def async_print_historical_protocol_tvl(
    protocol: str, verbose: bool = False
) -> None:

    styles = cli.get_cli_styles()

    uniswap = await llama_requests.async_get_historical_protocol_tvl(protocol)

    timestamp = []
    tvl = []
    for datum in uniswap['tvl']:
        timestamp.append(datum['date'])
        tvl.append(datum['totalLiquidityUSD'])

    plot = toolstr.render_line_plot(
        xvals=timestamp,
        yvals=tvl,
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
        yaxis_kwargs={'tick_label_format': {'prefix': '$'}},
    )

    toolstr.print_text_box(
        'Historical ' + protocol + ' TVL', style=styles['title']
    )
    print()

    if verbose:
        toolstr.print(
            toolstr.hjustify('All Chains', 'center', 70),
            indent=4,
            style=styles['title'],
        )
    toolstr.print(plot, indent=4)

    if verbose:
        chains = sorted(
            uniswap['currentChainTvls'].keys(),
            key=lambda chain: float(uniswap['currentChainTvls'][chain]),
            reverse=True,
        )

        print()
        for chain in chains:
            raw_data = uniswap['chainTvls'][chain]['tvl']
            timestamp = []
            tvl = []
            for datum in raw_data:
                timestamp.append(datum['date'])
                tvl.append(datum['totalLiquidityUSD'])

            plot = toolstr.render_line_plot(
                xvals=timestamp,
                yvals=tvl,
                n_rows=40,
                n_columns=120,
                line_style=styles['description'],
                chrome_style=styles['comment'],
                tick_label_style=styles['metavar'],
                yaxis_kwargs={'tick_label_format': {'prefix': '$'}},
            )
            print()
            toolstr.print(
                toolstr.hjustify(chain, 'center', 70),
                indent=4,
                style=styles['title'],
            )
            print()
            toolstr.print(
                plot,
                indent=4,
            )
            print()
