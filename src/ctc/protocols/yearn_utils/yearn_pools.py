from __future__ import annotations

import typing

import toolstr

from ctc.cli import cli_run
from . import yearn_web_api


async def async_summarize_pools(
    *,
    sort_by: str | None = None,
    min_tvl: int | float | None = None,
    min_apy: int | float | None = None,
    min_apr: int | float | None = None,
    n: int | None = 20,
) -> None:

    if sort_by is None:
        sort_by = 'gross APR'

    data = await yearn_web_api.async_request_yearn_api_v1_data()

    n_all_pools = len(data)

    # filter data
    n_clipped = 0
    filtered_data = []
    for datum in data:
        tvl = datum['tvl']['tvl']
        net_apy = datum['apy']['net_apy']
        gross_apr = datum['apy']['gross_apr']
        if (
            (min_tvl is not None and tvl < min_tvl)
            or (min_apy is not None and net_apy < min_apy)
            or (min_apr is not None and gross_apr < min_apr)
        ):
            n_clipped += 1
            continue
        filtered_data.append(datum)
    n_matching_pools = len(filtered_data)
    data = filtered_data

    # build rows
    labels = [
        'name',
        'TVL',
        'net APY',
        'gross APR',
    ]
    total_tvl = 0
    rows = []
    for datum in data:

        tvl = datum['tvl']['tvl']
        net_apy = datum['apy']['net_apy']
        gross_apr = datum['apy']['gross_apr']

        if tvl < 0.01:
            tvl = 0
        total_tvl += tvl

        row = [
            datum['display_name'],
            tvl,
            net_apy,
            gross_apr,
        ]
        rows.append(row)

    # sort rows
    sort_index = labels.index(sort_by)
    rows = sorted(rows, key=lambda row: row[sort_index], reverse=True)  # type: ignore

    # clip display rows
    if n is not None and len(rows) > n:
        rows = rows[:n]
        clip_row = ['...'] * len(labels)
        rows.append(clip_row)

    # add total row
    blank_row = [''] * len(labels)
    total_row: typing.List[typing.Any] = [''] * len(labels)
    total_row[labels.index('name')] = 'TOTAL'
    total_row[labels.index('TVL')] = total_tvl
    rows.append(blank_row)
    rows.append(total_row)

    # print outputs
    styles = cli_run.get_cli_styles()
    toolstr.print_text_box('Yearn Pool Summary', style=styles['title'])
    toolstr.print(
        'data obtained from https://api.yearn.finance', style=styles['comment']
    )
    if n_matching_pools != n_all_pools:
        print()
        toolstr.print(
            toolstr.add_style(str(n_matching_pools), styles['description'])
            + ' / '
            + toolstr.add_style(str(n_all_pools), styles['description'])
            + ' pools match input filters'
        )
    print()
    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'name': styles['metavar'],
            'TVL': styles['description'],
            'net APY': styles['description'],
            'gross APR': styles['description'],
        },
        indent=4,
        column_format={
            'TVL': {
                'order_of_magnitude': True,
                'trailing_zeros': True,
                'decimals': 2,
                'prefix': '$',
            },
            'net APY': {
                'percentage': True,
                'trailing_zeros': True,
                'decimals': 2,
            },
            'gross APR': {
                'percentage': True,
                'trailing_zeros': True,
                'decimals': 2,
            },
        },
    )
