from __future__ import annotations

import os

import toolcli
import toolstr
import tooltime

from ctc import cli
from ctc import evm
from ctc import spec
from ctc.cli import cli_utils
from ctc.toolbox.defi_utils import dex_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_trades_command,
        'help': 'get DEX swaps',
        'args': [
            {'name': 'pool', 'help': 'pool to retrieve swaps from'},
            {
                'name': ['-b', '--blocks'],
                'help': 'block range to retrieve swaps from',
            },
            {
                'name': '--no-normalize',
                'help': 'do not normalize by ERC20 decimals',
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
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'output extra data',
            },
        ],
        'examples': [
            '0xc5be99a02c6857f9eac67bbce58df5572498f40c --blocks 14000000:14010000',
        ],
    }


async def async_trades_command(
    *,
    pool: spec.Address,
    blocks: str,
    no_normalize: bool,
    export: str,
    overwrite: bool,
    verbose: bool,
) -> None:

    if blocks is not None:
        start_block, end_block = await cli_utils.async_parse_block_range(blocks)
    else:
        start_block = None
        end_block = None

    trades = await dex_utils.async_get_pool_trades(
        pool=pool,
        start_block=start_block,
        end_block=end_block,
        label='symbol',
        normalize=not no_normalize,
        include_prices=True,
        include_volumes=True,
    )

    if export is not None:
        if not overwrite and os.path.isfile(export):
            raise Exception('file already exists, use --overwrite')
        if export.endswith('.csv'):
            trades.to_csv(export)
        elif export.endswith('.json'):
            trades.to_json(export, orient='records')
        else:
            raise Exception('unknown export format')
    else:

        trades = trades.iloc[-100:]
        trades = trades.reset_index()

        block_timestamps = await evm.async_get_block_timestamps(
            trades['block_number']
        )
        trades['timestamp'] = [
            tooltime.timestamp_to_iso_pretty(timestamp)
            for timestamp in block_timestamps
        ]

        rename_columns = {
            key: key.replace('__', '\n') for key in list(trades.columns)
        }
        rename_columns['block_number'] = 'block'
        rename_columns['sold_id'] = 'sold'
        rename_columns['bought_id'] = 'bought'
        for key, value in rename_columns.items():
            if value.startswith('price\n'):
                rename_columns[key] = value[6:]
        trades = trades.rename(columns=rename_columns)

        columns = list(trades.columns)
        if not verbose:
            columns = [
                column
                for column in columns
                if column
                not in [
                    'transaction_hash',
                    'recipient',
                    'sold_amount',
                    'bought_amount',
                ]
            ]

        column_formats = {
            column: {'trailing_zeros': True, 'decimals': 2}
            for column in columns
        }
        column_formats['block'] = {'commas': False}

        styles = cli.get_cli_styles()
        column_styles = {
            'block': styles['metavar'],
            'sold': styles['option'],
            'bought': styles['option'],
        }
        for column in columns:
            if '\nper\n' in column or 'volume\n' in column:
                column_styles[column] = styles['description'] + ' bold'

        toolstr.print_dataframe_as_table(
            trades,
            columns=columns,
            compact=2,
            column_formats=column_formats,
            column_styles=column_styles,
            border=styles['comment'],
            include_index=False,
            label_style=styles['title'],
        )
