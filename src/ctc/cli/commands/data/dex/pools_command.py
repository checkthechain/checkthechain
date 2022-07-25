"""
TODO:
- colors
- filter by platform
- implement TVLs
"""
from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc.cli import cli_run
from ctc import db
from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_dex_pools_command,
        'help': 'list dex pools',
        'args': [
            {
                'name': 'token',
                'help': 'token symbol or address',
                'nargs': '?',
            },
            {
                'name': '--platform',
                'help': 'name of platform (e.g. balancer, curve, uniswap-v2',
            },
            {
                'name': '--all',
                'help': 'display all pools instead of just the first 1000',
                'dest': 'all_pools',
                'action': 'store_true',
            },
            {
                'name': '--compact',
                'help': 'use compact view for higher information density',
                'action': 'store_true',
            },
        ],
        'examples': [
            'CRV',
            'DAI --platform balancer',
        ],
    }


platforms = {
    '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f': 'Uniswap V2',
    '0x1f98431c8ad98523631ae4a59f267346ea31f984': 'Uniswap V3',
    '0xba12222222228d8ba445958a75a0704d566bf2c8': 'Balancer',
    '0xb9fc157394af804a3578134a6585c0dc9cc990d4': 'Curve',
    '0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac': 'Sushi',
}


def simplify_name(name: str) -> str:
    return name.lower().replace('-', '').replace(' ', '').replace('_', '')


async def async_dex_pools_command(
    *,
    token: spec.Address | str,
    platform: spec.Address | str,
    all_pools: bool,
    compact: bool,
) -> None:

    if token is not None:
        if evm.is_address_str(token):
            address = token
        else:
            address = await evm.async_get_erc20_address(token)
        assets = [address]
    else:
        assets = None

    if platform is not None:

        simple_platform = simplify_name(platform)
        for factory, factory_name in platforms.items():
            factory_name = simplify_name(factory_name)
            if simple_platform == factory_name:
                break
        else:
            raise Exception('unknown platform: ' + str(platform))
    else:
        factory = None

    dex_pools = await db.async_get_known_dex_pools(assets=assets, factory=factory)

    styles = cli_run.get_cli_styles()

    toolstr.print(
        toolstr.add_style(str(len(dex_pools)), styles['description'] + ' bold'),
        'pools found',
    )
    print()

    max_pools = 1000
    if len(dex_pools) > max_pools and not all_pools:
        clipped = len(dex_pools) - max_pools
        dex_pools = dex_pools[:max_pools]
    else:
        clipped = 0

    all_assets: set[str | None] = set()
    n_assets = 2
    for dex_pool in dex_pools:
        all_assets.add(dex_pool['asset0'])
        all_assets.add(dex_pool['asset1'])

        asset2 = dex_pool['asset2']
        if asset2 is not None:
            all_assets.add(dex_pool['asset2'])
            n_assets = 3

        asset3 = dex_pool['asset3']
        if asset3 is not None:
            all_assets.add(dex_pool['asset3'])
            n_assets = 4

    ordered_assets = [asset for asset in all_assets if asset is not None]
    symbols = await evm.async_get_erc20s_symbols(
        ordered_assets,
        provider={'chunk_size': 10, 'convert_reverts_to_none': True},
    )

    symbols = [symbol.replace('\x00', '') for symbol in symbols]

    assets_to_symbols: typing.Mapping[str | None, str] = dict(
        zip(ordered_assets, symbols)
    )

    rows = []
    for dex_pool in dex_pools:
        row: list[str | None] = [
            dex_pool['address'],
            platforms.get(dex_pool['factory']),
            assets_to_symbols.get(dex_pool['asset0']),
            assets_to_symbols.get(dex_pool['asset1']),
        ]
        if n_assets >= 3:
            row.append(assets_to_symbols.get(dex_pool['asset2'], ''))
        if n_assets >= 4:
            row.append(assets_to_symbols.get(dex_pool['asset3'], ''))

        rows.append(row)

    labels = [
        'address',
        'platform',
        'asset0',
        'asset1',
    ]
    if n_assets >= 3:
        labels.append('asset2')
    if n_assets >= 4:
        labels.append('asset3')

    sort_indices = [
        labels.index('platform'),
        labels.index('asset0'),
        labels.index('asset1'),
    ]
    rows = sorted(
        rows, key=lambda row: tuple(row[index] for index in sort_indices)
    )

    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_style={
            'address': styles['metavar'],
            'asset0': styles['description'] + ' bold',
            'asset1': styles['description'] + ' bold',
            'asset2': styles['description'] + ' bold',
            'asset3': styles['description'] + ' bold',
        },
        max_table_width=toolcli.get_n_terminal_cols(),
        compact=compact,
    )

    if clipped:
        print()
        toolstr.print(
            'showing only first',
            max_pools,
            'pools, use',
            toolstr.add_style('--all', styles['option']),
            'to display all',
            clipped + max_pools,
            'pools',
            style=styles['comment'],
        )
