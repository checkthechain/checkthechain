from __future__ import annotations

import asyncio
import typing

import toolcli
import toolstr

from ctc.cli import cli_run
from ctc.cli import cli_utils
from ctc import evm
from ctc import spec
from ctc.toolbox.defi_utils import dex_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_dex_pools_command,
        'help': 'list dex pools',
        'args': [
            {
                'name': 'tokens',
                'help': 'token symbols or addresses (separate using spaces)',
                'nargs': '*',
            },
            {
                'name': '--platform',
                'help': 'name of platform (e.g. balancer, curve, uniswap-v2',
            },
            {
                'name': '--all-pools',
                'help': 'display all pools instead of just the first 1000',
                'action': 'store_true',
            },
            {
                'name': '--compact',
                'help': 'use compact view for higher information density',
                'action': 'store_true',
            },
            {
                'name': ['--verbose', '-v'],
                'help': 'show additional data',
                'action': 'store_true',
            },
            {
                'name': '--json',
                'help': 'output data as json',
                'dest': 'json_output',
                'action': 'store_true',
            },
            {
                'name': '--csv',
                'help': 'output data as json',
                'dest': 'csv_output',
                'action': 'store_true',
            },
            {
                'name': '--output',
                'help': 'file path to save output to',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {
                'name': '--sort',
                'help': 'column to sort pools by',
                'nargs': '+',
            },
        ],
        'examples': [
            'CRV',
            'DAI --platform balancer',
        ],
    }


def simplify_name(name: str) -> str:
    return name.lower().replace('-', '').replace(' ', '').replace('_', '')


async def async_dex_pools_command(
    *,
    tokens: typing.Sequence[spec.Address | str],
    platform: spec.Address | str,
    all_pools: bool,
    compact: bool,
    verbose: bool,
    json_output: bool,
    csv_output: bool,
    output: str | None,
    overwrite: bool,
    sort: typing.Sequence[str] | None,
) -> None:

    platforms = dex_utils.get_dex_pool_factory_platforms(network='mainnet')

    coroutines = [evm.async_get_erc20_address(token) for token in tokens]
    assets = await asyncio.gather(*coroutines)

    factories: typing.Sequence[spec.Address] | None
    if platform is not None:

        factory = None

        use_factories = []
        simple_platform = simplify_name(platform)
        for factory, factory_name in platforms.items():
            factory_name = simplify_name(factory_name)
            if simple_platform == factory_name:
                use_factories.append(factory)

        if len(use_factories) > 1:
            factories = use_factories
            factory = None
        elif len(use_factories) == 1:
            factory = use_factories[0]
            factories = None
        else:
            raise Exception('unknown platform: ' + str(platform))
    else:
        factory = None
        factories = None

    dex_pools = await dex_utils.async_get_dex_pools(
        assets=assets,
        factory=factory,
        factories=factories,
    )

    # alternative output formats
    if json_output and output is None:
        import json

        as_str = json.dumps(dex_pools)
        print(as_str)
        return
    if csv_output and output is None:
        import pandas as pd

        df = pd.DataFrame(dex_pools)
        csv_str = df.to_csv()
        print(csv_str)
        return
    if output:
        import pandas as pd

        df = pd.DataFrame(dex_pools)
        cli_utils.output_data(df, output=output, overwrite=overwrite)
        print('saved output to', output)
        return

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

    # get block times
    if verbose:
        import tooltime

        all_blocks = list(
            {dex_pool['creation_block'] for dex_pool in dex_pools}
        )
        block_timestamps = await evm.async_get_block_timestamps(all_blocks)
        timestamps_of_blocks = dict(zip(all_blocks, block_timestamps))

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

        if verbose:
            block = dex_pool['creation_block']
            timestamp = timestamps_of_blocks[block]
            age = tooltime.get_age(timestamp, 'TimelengthPhrase')
            age = ' '.join(age.split(' ')[:2]).strip(',')

            row.append(str(block))
            row.append(age)

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
    if verbose:
        labels.append('creation\nblock')
        labels.append('age')

    if sort is not None:
        sort_indices = [
            labels.index(column)
            for column in sort
        ]
    else:
        sort_indices = [
            labels.index('platform'),
            labels.index('asset0'),
            labels.index('asset1'),
        ]
    rows = sorted(
        rows,
        key=lambda row: tuple(
            row[index] if row[index] else '' for index in sort_indices
        ),
    )

    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
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
