from __future__ import annotations

import asyncio
import typing

import toolcli
import toolstr

from ctc import cli
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
                'name': '--update',
                'help': 'run update to index all recently created pools',
                'action': 'store_true',
            },
            {
                'name': '--created',
                'help': 'specify start and/or end of when pool was created',
            },
            {
                'name': '--dex',
                'help': 'name of dex (e.g. balancer, curve, uniswap-v2)',
            },
            {
                'name': '--factory',
                'help': 'address of pool factory',
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
                'name': '--export',
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
            'DAI --dex balancer',
            'DAI --created 14000000:15000000',
        ],
    }


def simplify_name(name: str) -> str:
    return name.lower().replace('-', '').replace(' ', '').replace('_', '')


async def async_dex_pools_command(
    *,
    tokens: typing.Sequence[spec.Address | str],
    dex: spec.Address | str | None,
    update: bool,
    created: str | None,
    factory: spec.Address | None,
    all_pools: bool,
    compact: bool,
    verbose: bool,
    json_output: bool,
    csv_output: bool,
    export: str | None,
    overwrite: bool,
    sort: typing.Sequence[str] | None,
) -> None:

    factory_dexes = dex_utils.get_dex_names_of_factories(network='mainnet')

    coroutines = [evm.async_get_erc20_address(token) for token in tokens]
    assets = await asyncio.gather(*coroutines)

    if created is not None:
        start_block, end_block = await cli_utils.async_parse_block_range(created)
    else:
        start_block = None
        end_block = None
    dex_pools = await dex_utils.async_get_pools(
        assets=assets,
        factory=factory,
        dex=dex,
        start_block=start_block,
        end_block=end_block,
        update=update,
    )

    # alternative output formats
    if json_output and export is None:
        import json

        as_str = json.dumps(dex_pools)
        print(as_str)
        return
    if csv_output and export is None:
        import pandas as pd

        df = pd.DataFrame(dex_pools)
        csv_str = df.to_csv()
        print(csv_str)
        return
    if export:
        import pandas as pd

        df = pd.DataFrame(dex_pools)
        cli_utils.output_data(df, output=export, overwrite=overwrite)
        print('saved output to', export)
        return

    styles = cli.get_cli_styles()

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

    for i in range(len(ordered_assets)):
        if ordered_assets[i] == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
            symbols[i] = 'ETH'
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
            factory_dexes.get(dex_pool['factory']),
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
        'dex',
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
            labels.index('dex'),
            labels.index('asset0'),
            labels.index('asset1'),
        ]
    rows = sorted(
        rows,
        key=lambda row: tuple(
            row[index] if row[index] else '' for index in sort_indices
        ),
    )

    if not verbose:
        max_column_widths: typing.Mapping[str | int, int] | None = {
            'asset0': 10,
            'asset1': 10,
            'asset2': 10,
            'asset3': 10,
        }
    else:
        max_column_widths = None

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
        max_column_widths=max_column_widths,
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
