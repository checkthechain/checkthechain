from __future__ import annotations

import typing

import toolcli
import toolstr

import ctc.config
from ctc import cli
from ctc import evm
from ctc import spec
from ctc.cli import cli_utils


command_help = """output ERC20 total supply of blocks"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_total_supply_command,
        'help': command_help,
        'args': [
            {'name': 'erc20', 'help': 'address of ERC20 token'},
            {
                'name': '--blocks',
                'nargs': '+',
                'help': 'block numbers to get total supply at',
            },
            #
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'whether to skip normalizing by ERC20 decimals',
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
            {'name': '-n', 'help': 'show n data points', 'type': int},
        ],
        'examples': {
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0x9928e4046d7c6513326ccea028cd3e7a91c7590a --blocks 14000000:14000100',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0x9928e4046d7c6513326ccea028cd3e7a91c7590a --blocks 14000000:14000100 --raw'
        },
    }


async def async_total_supply_command(
    *,
    erc20: spec.Address,    
    blocks: typing.Sequence[str],
    raw: bool,
    export: str,
    overwrite: bool,
    n: int | None,
) -> None:

    import polars as pl

    resolved_blocks = await cli_utils.async_parse_block_slice(blocks, n=n)

    timestamps = await evm.async_get_block_timestamps(resolved_blocks)

    erc20 = await evm.async_resolve_address(
        erc20, block=resolved_blocks[-1]
    )
    total_supplies = await evm.async_get_erc20_total_supply_by_block(
        token=erc20,
        blocks=resolved_blocks,
        normalize=(not raw)
    )

    if export == 'stdout':
        styles = cli.get_cli_styles()

        # print header
        toolstr.print_text_box(
            'Historical ERC20 Total Supply', style=styles['title']
        )
        print()
        toolstr.print_table(
            rows=[['token', erc20]],
            column_justify=['right', 'left'],
            border=styles['comment'],
            column_styles=[styles['option'], styles['metavar']],
        )

        import tooltime

        # print balance history table
        print()
        print()
        rows = []
        for block, timestamp, total_supply in zip(resolved_blocks, timestamps, total_supplies):
            age = tooltime.get_age(timestamp, 'TimelengthPhrase')
            age = ', '.join(age.split(', ')[:1])
            row = [tooltime.timestamp_to_iso(timestamp), age, block, total_supply]
            rows.append(row)
        labels = ['timestamp', 'age', 'block', 'total supply']
        if n is None:
            n = 21
        toolstr.print_table(
            rows,
            labels=labels,
            border=styles['comment'],
            label_style=styles['title'],
            column_formats={'balance': {'order_of_magnitude': True, 'trailing_zeros': True}},
            column_styles={
                'balance': styles['description'] + ' bold',
            },
            # indent=4,
            limit_rows=n,
        )

        # print balance history chart
        def formatter(xval: typing.Any) -> str:
            return toolstr.format(round(xval))

        xvals = resolved_blocks
        yvals = total_supplies
        plot = toolstr.render_line_plot(
            xvals=xvals,
            yvals=yvals,
            n_rows=10,
            n_columns=60,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            xaxis_kwargs={'formatter': formatter},
            char_dict=ctc.config.get_cli_chart_charset(),
        )
        print()
        print()
        toolstr.print(
            toolstr.hjustify('ERC20 total supply over time', 'center', 70),
            indent=4,
            style=styles['title'],
        )
        toolstr.print(plot, indent=4)

        return

    else:
        df = pl.DataFrame({'balance': total_supply, 'block': resolved_blocks})
        output_data = df


    cli_utils.output_data(
        output_data,
        output=export,
        overwrite=overwrite,
        top=n
    )
