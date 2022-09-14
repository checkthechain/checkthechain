from __future__ import annotations

import typing

import toolcli
import tooltime
import toolstr

from ctc import cli
from ctc import evm
from ctc import rpc
from ctc import spec

from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_blocks_command,
        'help': 'output information about blocks',
        'args': [
            {'name': 'blocks', 'nargs': '+', 'help': 'block range to fetch'},
            {
                'name': '-n',
                'help': 'number of blocks in block slice',
                'type': int,
            },
            {
                'name': '--attributes',
                'nargs': '+',
                'help': 'attributes to fetch from each block',
            },
            {
                'name': '--export',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {'name': '--provider', 'help': 'rpc provider to use'},
        ],
        'examples': {
            '14000000:14000010': 'get blocks 14000000 through 14000010',
            '14000000:15000000:100000': 'get blocks 14000000 through 15000000, every 100000 blocks',
            '14000000:15000000 -n 10': 'get blocks 14000000 through 15000000, every 100000 blocks',
            '14000000:14000100 --attributes timestamp,number': 'get blocks 14000000 through 14000100, with specific attributes',
        },
    }


async def async_blocks_command(
    *,
    blocks: typing.Sequence[str],
    n: int | None,
    attributes: typing.Optional[typing.Sequence[str]],
    export: str,
    overwrite: bool,
    provider: typing.Optional[str],
) -> None:
    import pandas as pd

    if attributes is None:
        # gas stats as well
        attributes = [
            'number',
            'timestamp',
            'age',
            'median_gas',
        ]
    elif attributes == ['all']:
        attributes = list(spec.block_keys)
    else:
        attributes = [
            attribute for token in attributes for attribute in token.split(',')
        ]

    # determine blocks
    # export_blocks = await cli_utils.async_resolve_block_range(blocks)
    export_blocks = await cli_utils.async_parse_block_slice(blocks, n=n)

    # print summary
    styles = cli.get_cli_styles()
    toolstr.print_text_box('Blocks Data', style=styles['title'])
    cli.print_bullet(key='n_blocks', value=len(export_blocks))
    cli.print_bullet(key='min block', value=min(export_blocks))
    cli.print_bullet(key='max block', value=max(export_blocks))

    blocks_data = await rpc.async_batch_eth_get_block_by_number(
        block_numbers=export_blocks,
        include_full_transactions=True,
        provider=provider,
    )

    if export == 'stdout':
        cli.print_bullet(key='attributes', value='')
        for attribute in attributes:
            cli.print_bullet(value=attribute, indent=4)
        print()

        aliases = {
            'number': 'block',
            'median_gas': 'median gas',
        }
        rows = []
        for block in blocks_data:
            row: list[typing.Any] = []
            for attribute in attributes:
                if attribute == 'timestamp':
                    row.append(
                        tooltime.timestamp_to_iso_pretty(block['timestamp'])
                    )
                elif attribute == 'age':
                    age = tooltime.get_age(
                        block['timestamp'], 'TimelengthPhrase'
                    )
                    age = ', '.join(age.split(', ')[:2])
                    row.append(age)
                elif attribute == 'median_gas':
                    median_gas = evm.compute_median_block_gas_fee(
                        block, normalize=True
                    )
                    row.append(median_gas)
                else:
                    row.append(block[attribute])
            rows.append(row)
        labels = [aliases.get(attribute, attribute) for attribute in attributes]
        print()
        toolstr.print_table(
            rows,
            labels=labels,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'block': styles['description'],
            },
            column_formats={
                'block': {'commas': False},
                'median gas': {'postfix': ' gwei', 'trailing_zeros': True},
            },
            compact=4,
        )
    else:

        # format as dataframe
        df = pd.DataFrame(blocks_data)

        # # special attribute: time
        # if 'time' in attributes:
        #     df['time'] = df['timestamp'].map(tooltime.timestamp_to_iso)

        # # trim attributes
        # if len(attributes) > 0:
        #     df = df[attributes]

        # # output data
        # if 'number' in df:
        #     df = df.set_index('number')
        cli_utils.output_data(df, output=export, overwrite=overwrite)
