from __future__ import annotations

import typing

from typing_extensions import Literal

import toolstr

from ctc import cli
from . import llama_requests


#
# # pool comparison and aggregation
#


async def async_print_llama_pools_summary(
    *,
    chain: str | None = None,
    project: str | None = None,
    stablecoin: bool | None = None,
    exposure: Literal['single', 'multi'] | None = None,
    min_apy: typing.SupportsFloat | None = None,
    max_apy: typing.SupportsFloat | None = None,
    min_tvl: typing.SupportsFloat | None = None,
    max_tvl: typing.SupportsFloat | None = None,
    n: int | None = None,
    verbose: bool = False,
    show_id: bool = False,
) -> None:

    if n is None:
        n = 15

    pools = await llama_requests.async_get_llama_pools(
        chain=chain,
        project=project,
        stablecoin=stablecoin,
        exposure=exposure,
        min_apy=min_apy,
        max_apy=max_apy,
        min_tvl=min_tvl,
        max_tvl=max_tvl,
    )

    styles = cli.get_cli_styles()

    toolstr.print_text_box('Defi Llama Tracked Pools', style=styles['title'])

    filter_items = [
        chain,
        project,
        stablecoin,
        exposure,
        min_apy,
        max_apy,
        min_tvl,
        max_tvl,
    ]
    if any(item is not None for item in filter_items):
        print()
        toolstr.print('filters:', style=styles['option'])
    if chain is not None:
        toolstr.print(
            '    chain=' + toolstr.add_style(chain, styles['description']),
            style=styles['option'],
        )
    if project is not None:
        toolstr.print(
            '    project=' + toolstr.add_style(project, styles['description']),
            style=styles['option'],
        )
    if stablecoin is not None:
        toolstr.print(
            '    stablecoin='
            + toolstr.add_style(str(stablecoin), styles['description']),
            style=styles['option'],
        )
    if exposure is not None:
        toolstr.print(
            '    exposure='
            + toolstr.add_style(exposure, styles['description']),
            style=styles['option'],
        )
    if min_apy is not None:
        toolstr.print(
            '    min_apy='
            + toolstr.add_style(str(min_apy), styles['description']),
            style=styles['option'],
        )
    if max_apy is not None:
        toolstr.print(
            '    max_apy='
            + toolstr.add_style(str(max_apy), styles['description']),
            style=styles['option'],
        )
    if min_tvl is not None:
        toolstr.print(
            '    min_tvl='
            + toolstr.add_style(str(min_tvl), styles['description']),
            style=styles['option'],
        )
    if max_tvl is not None:
        toolstr.print(
            '    max_tvl='
            + toolstr.add_style(str(max_tvl), styles['description']),
            style=styles['option'],
        )

    print()
    toolstr.print(
        toolstr.add_style(str(len(pools)), styles['description'] + ' bold')
        + ' pools found'
    )
    if verbose:
        print_pool_counts_summary(pools)

    highest_apy_pools = sorted(
        pools, key=lambda pool: float(pool['apy']), reverse=True
    )
    highest_tvl_pools = sorted(
        pools, key=lambda pool: float(pool['tvlUsd']), reverse=True
    )

    print()
    print()
    toolstr.print('Highest APY pools', style=styles['title'])
    print()
    print_pools_table(
        pools=highest_apy_pools,
        n=n,
        show_id=show_id,
    )

    print()
    print()
    toolstr.print('Highest TVL pools', style=styles['title'])
    print()
    print_pools_table(
        pools=highest_tvl_pools,
        n=n,
        show_id=show_id,
    )


def print_pools_table(
    *,
    pools: typing.Sequence[typing.Any],
    n: int,
    show_id: bool = False,
) -> None:

    styles = cli.get_cli_styles()

    labels = [
        'symbol',
        'chain',
        'project',
        'apy',
        'tvl',
    ]
    if show_id:
        labels.append('id')

    rows = []
    for pool in pools[:n]:
        row = [
            pool['symbol'],
            pool['chain'],
            pool['project'],
            pool['apy'],
            pool['tvlUsd'],
        ]
        if show_id:
            row.append(pool['pool'])
        rows.append(row)

    if len(pools) > n:
        rows.append(['...'] * len(labels))

    toolstr.print_table(
        rows,
        labels=labels,
        max_column_widths={'pool': 45},
        column_formats={
            'apy': {'postfix': '%', 'decimals': 2, 'trailing_zeros': True},
            'tvl': {
                'order_of_magnitude': True,
                'prefix': '$',
                'decimals': 2,
                'trailing_zeros': True,
            },
        },
        indent=4,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'symbol': styles['option'],
            'chain': styles['option'],
            'project': styles['option'],
            'apy': styles['description'],
            'tvl': styles['description'],
        },
    )


def print_pool_counts_summary(
    pools: typing.Sequence[typing.Any],
    n: int = 10,
) -> None:

    chain_pool_counts: typing.MutableMapping[str, float | int] = {}
    project_pool_counts: typing.MutableMapping[str, float | int] = {}
    stablecoin_pool_counts: typing.MutableMapping[bool, float | int] = {}

    chain_pool_tvls: typing.MutableMapping[str, float | int] = {}
    project_pool_tvls: typing.MutableMapping[str, float | int] = {}
    stablecoin_pool_tvls: typing.MutableMapping[bool, float | int] = {}

    for pool in pools:

        chain = pool['chain']
        chain_pool_counts.setdefault(chain, 0)
        chain_pool_counts[chain] += 1
        chain_pool_tvls.setdefault(chain, 0)
        chain_pool_tvls[chain] += pool['tvlUsd']

        project = pool['project']
        project_pool_counts.setdefault(project, 0)
        project_pool_counts[project] += 1
        project_pool_tvls.setdefault(project, 0)
        project_pool_tvls[project] += pool['tvlUsd']

        stablecoin = pool['stablecoin']
        stablecoin_pool_counts.setdefault(stablecoin, 0)
        stablecoin_pool_counts[stablecoin] += 1
        stablecoin_pool_tvls.setdefault(stablecoin, 0)
        stablecoin_pool_tvls[stablecoin] += pool['tvlUsd']

    project_pool_counts = dict(
        sorted(
            project_pool_counts.items(), key=lambda item: item[1], reverse=True
        )
    )
    chain_pool_counts = dict(
        sorted(
            chain_pool_counts.items(), key=lambda item: item[1], reverse=True
        )
    )

    money_format: toolstr.NumberFormat = {
        'order_of_magnitude': True,
        'decimals': 2,
        'trailing_zeros': True,
        'prefix': '$',
    }

    styles = cli.get_cli_styles()

    toolstr.print(
        '- stablecoin pools: '
        + toolstr.add_style(
            str(stablecoin_pool_counts[True]), styles['description'] + ' bold'
        ),
    )
    toolstr.print(
        '- stablecoin TVL:',
        toolstr.add_style(
            toolstr.format(stablecoin_pool_tvls[True], **money_format),
            styles['description'] + ' bold',
        ),
    )
    print()
    print()
    toolstr.print('Projects with most pools', style=styles['title'])
    print()
    rows = []
    for project, count in list(project_pool_counts.items())[:n]:
        row = [project, count, project_pool_tvls[project]]
        rows.append(row)
    if len(project_pool_counts) > n:
        rows.append(['...', '...', '...'])
    toolstr.print_table(
        rows,
        labels=['project', 'pools', 'tvl'],
        indent=4,
        column_formats={
            'tvl': money_format,
        },
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'project': styles['option'],
            'pools': styles['description'],
            'tvl': styles['description'],
        },
    )

    print()
    print()
    toolstr.print('Chains with most pools', style=styles['title'])
    print()
    rows = []
    for chain, count in list(chain_pool_counts.items())[:n]:
        row = [chain, count, chain_pool_tvls[chain]]
        rows.append(row)
    if len(chain_pool_counts) > n:
        rows.append(['...', '...', '...'])
    toolstr.print_table(
        rows,
        labels=['chain', 'pools', 'tvl'],
        indent=4,
        column_formats={
            'tvl': money_format,
        },
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'chain': styles['option'],
            'pools': styles['description'],
            'tvl': styles['description'],
        },
    )


#
# # individual pool examination
#


async def async_print_pool_yield_summary(pool: typing.Any) -> None:

    styles = cli.get_cli_styles()

    data = await llama_requests.async_get_pool_yield(pool)

    toolstr.print_text_box(
        'Pool ' + pool + ' History',
        style=styles['title'],
    )
    print()

    plot = toolstr.render_line_plot(
        xvals=data['timestamp'],
        yvals=data['apy'],
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
        yaxis_kwargs={'tick_label_format': {'postfix': '%'}},
    )
    toolstr.print(
        toolstr.hjustify('APY', 'center', 70),
        indent=4,
        style=styles['title'],
    )
    toolstr.print(plot, indent=4)
    print()

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
    toolstr.print(
        toolstr.hjustify('TVL', 'center', 70),
        indent=4,
        style=styles['title'],
    )
    toolstr.print(plot, indent=4)
