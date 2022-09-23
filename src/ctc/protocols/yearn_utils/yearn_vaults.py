from __future__ import annotations

import asyncio
import typing

import toolstr
import tooltime

from ctc import evm
from ctc import spec
from ctc import cli
from . import yearn_web_api
from . import yearn_strategies


async def async_search_single_vault_address(
    query: str,
    network: spec.NetworkReference,
) -> spec.Address:

    if evm.is_address_str(query):
        return query.lower()
    else:
        vault = await yearn_web_api.async_get_yearn_api_vault(
            query=query,
            network=network,
        )
        return vault['address']


async def async_print_vault_summary(
    query: str,
    network: spec.NetworkReference,
    *,
    verbose: bool = False,
    show_harvests: int | bool | None = None,
) -> None:

    obtained = tooltime.create_timestamp_iso_pretty()
    vault = await yearn_web_api.async_get_yearn_api_vault(
        query, network=network
    )

    styles = cli.get_cli_styles()

    toolstr.print_text_box(
        'Yearn Vault ' + vault['name'], style=styles['title']
    )

    print()
    toolstr.print_header('Vault Addresses', style=styles['title'])
    rows = [
        ['vault', vault['address'].lower()],
        ['token', vault['token']['address'].lower()],
    ]
    # if 'migration' in vault:
    #     rows.append(['migration', vault['migration']['address'].lower()])
    for strategy in vault['strategies']:
        rows.append([strategy['name'], strategy['address'].lower()])
    print()
    toolstr.print_table(
        rows,
        indent=4,
        border=styles['comment'],
        column_styles=[styles['option'], styles['metavar']],
    )

    inception_timestamp = await evm.async_get_block_timestamp(
        vault['inception']
    )
    age = tooltime.get_age(inception_timestamp, 'TimelengthPhrase')
    rough_age = ', '.join(age.split(', ')[:2])

    print()
    print()
    toolstr.print_header('Vault Metadata', style=styles['title'])
    print()
    rows = [
        ['name', vault['name']],
        ['display name', vault['display_name']],
        ['symbol', vault['symbol']],
        ['version', vault['version']],
        ['type', vault['type']],
        ['decimals', vault['decimals']],
        ['inception block', str(vault['inception'])],
        ['age', rough_age],
    ]
    if verbose:
        fees = vault['apy']['fees']
        rows.append(
            [
                'management fee',
                toolstr.format(fees['management'], percentage=True),
            ]
        )
        rows.append(
            [
                'performance fee',
                toolstr.format(fees['performance'], percentage=True),
            ]
        )
        if vault['apy']['type'] == 'crv':
            rows.append(
                ['keep CRV', toolstr.format(fees['keep_crv'], percentage=True)]
            )
            rows.append(
                [
                    'CVX keep CRV',
                    toolstr.format(fees['cvx_keep_crv'], percentage=True),
                ]
            )

    toolstr.print_table(
        rows,
        indent=4,
        border=styles['comment'],
        column_styles=[styles['option'], styles['description']],
    )

    if verbose:
        print()
        print()
        toolstr.print_header('Token Metadata', style=styles['title'])
        print()
        rows = [
            ['token name', vault['token']['name']],
            ['token display name', vault['token']['display_name']],
            ['token symbol', vault['token']['symbol']],
            ['token decimals', vault['token']['decimals']],
        ]
        toolstr.print_table(
            rows,
            indent=4,
            border=styles['comment'],
            column_styles=[styles['option'], styles['description']],
        )

    print()
    print()
    toolstr.print_header('Vault State', style=styles['title'])
    print()
    tvl = toolstr.format(
        vault['tvl']['tvl'],
        prefix='$',
        decimals=2,
        trailing_zeros=True,
        order_of_magnitude=True,
    )
    gross_apr = toolstr.format(
        vault['apy']['gross_apr'],
        percentage=True,
        decimals=3,
        trailing_zeros=True,
    )
    net_apy = toolstr.format(
        vault['apy']['net_apy'],
        percentage=True,
        decimals=3,
        trailing_zeros=True,
    )

    rows = [
        ['TVL', tvl],
        ['gross APR', gross_apr],
        ['net APY', net_apy],
    ]
    if verbose:
        rows.append(['APR type', vault['apy']['type']])
        rows.append(['is shutdown', vault['emergency_shutdown']])
        rows.append(
            ['last updated', tooltime.timestamp_to_iso_pretty(vault['updated'])]
        )
    toolstr.print_table(
        rows,
        indent=4,
        border=styles['comment'],
        column_styles=[styles['option'], styles['description']],
    )

    # display harvests data
    # TODO: this is very unoptimized, wait until after event db overhaul is complete
    if show_harvests not in [None, False]:

        print()
        print()
        toolstr.print_header('Recent Harvests', style=styles['title'])

        if isinstance(show_harvests, bool):
            n_harvests = 10
        elif isinstance(show_harvests, int):
            n_harvests = show_harvests
        else:
            raise Exception('unknown format for show_harvests parameter')

        strategies = [strategy['address'] for strategy in vault['strategies']]
        strategy_address_to_name = {
            strategy['address'].lower(): strategy['name']
            for strategy in vault['strategies']
        }
        try:
            coroutines = [
                yearn_strategies.async_get_harvests(strategy=strategy)
                for strategy in strategies
            ]
            import pandas as pd

            all_harvests = pd.concat(await asyncio.gather(*coroutines))
            all_harvests = all_harvests.sort_index()
        except Exception:
            print()
            toolstr.print(
                'could not obtain harvests',
                style=styles['content'],
                indent=4,
            )
            all_harvests = pd.DataFrame()
        rows = []
        for block, harvest in all_harvests.iloc[-n_harvests:].iterrows():
            age = tooltime.get_age(harvest['timestamp'], 'TimelengthPhrase')
            age = ', '.join(age.split(', ')[:1])
            row = [
                age,
                harvest['apr'],
                strategy_address_to_name[harvest['contract_address']],
            ]
            rows.append(row)
        labels = [
            'age',
            'apr',
            'strategy',
        ]
        print()
        toolstr.print_table(
            rows=rows,
            labels=labels,
            indent=4,
            column_formats={
                'apr': {
                    'percentage': True,
                    'trailing_zeros': True,
                    'decimals': 3,
                },
            },
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'age': styles['description'],
                'apr': styles['description'],
                'strategy': styles['metavar'],
            },
        )

    print()
    toolstr.print(
        'data from Yearn web API at ' + obtained,
        style=styles['comment'],
    )


async def async_print_vaults_summary(
    *,
    network: spec.NetworkReference,
    sort_by: str | None = None,
    min_tvl: int | float | None = None,
    min_apy: int | float | None = None,
    min_apr: int | float | None = None,
    n: int | None = 20,
    verbose: bool = False,
) -> None:

    if sort_by is None:
        sort_by = 'gross APR'

    api_vaults = await yearn_web_api.async_get_yearn_api_vaults(network=network)

    n_all_vaults = len(api_vaults)

    # filter data
    n_clipped = 0
    filtered_data = []
    for datum in api_vaults:
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
    n_matching_vaults = len(filtered_data)
    data = filtered_data

    # build rows
    labels = [
        'name',
        'TVL',
        'net APY',
        'gross APR',
    ]
    if verbose:
        labels.append('address')
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
            datum['name'],
            tvl,
            net_apy,
            gross_apr,
        ]
        if verbose:
            row.append(datum['address'].lower())
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
    styles = cli.get_cli_styles()
    toolstr.print_text_box('Yearn Pool Summary', style=styles['title'])
    toolstr.print(
        'data obtained from https://api.yearn.finance', style=styles['comment']
    )
    if n_matching_vaults != n_all_vaults:
        print()
        toolstr.print(
            toolstr.add_style(str(n_matching_vaults), styles['description'])
            + ' / '
            + toolstr.add_style(str(n_all_vaults), styles['description'])
            + ' vaults match input filters'
        )
    print()
    if verbose:
        indent = None
    else:
        indent = 4
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
            'address': styles['metavar'],
        },
        indent=indent,
        column_formats={
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
        compact=verbose,
    )
