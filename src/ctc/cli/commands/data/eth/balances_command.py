"""
# balances of wallets within single block
ctc eth balances <wallets> [--block <block>]

# balance of single wallet across multiple blocks
ctc eth balances <wallet> [--blocks <block>]
"""

from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import spec
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_balances_command,
        'help': 'output ETH balance across blocks or addresses',
        'args': [
            {
                'name': 'wallets',
                'nargs': '+',
                'help': 'wallet addresses to get balances of',
            },
            {'name': '--block', 'help': 'block number'},
            {
                'name': '--blocks',
                'nargs': '+',
                'help': 'block numbers to get balances in',
            },
            #
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'skip normalizing by 1e18 decimals',
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
            {
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'display additional information',
            },
        ],
        'examples': {
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 0xea674fdde714fd979de3edf0f56aa9716b898ec8 0xbe0eb53f46cd790cd13851d5eff43d12404d33e8': 'multiple wallets',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 --blocks 14000000:14000100': 'multiple blocks',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 -v --blocks 14000000:14100000:1000': 'multiple blocks with USD values',
        },
    }


async def async_balances_command(
    *,
    wallets: typing.Sequence[str],
    block: typing.Optional[spec.BlockNumberReference],
    blocks: typing.Optional[typing.Sequence[str]],
    raw: bool,
    export: str,
    overwrite: bool,
    verbose: bool,
) -> None:

    # REMOVE this
    import pandas as pd

    indent = None
    wallets = [wallet.lower() for wallet in wallets]

    if blocks is not None:
        # single wallet, multiple blocks
        if len(wallets) > 1:
            raise Exception(
                'cannot specify multiple wallets and multiple blocks'
            )

        resolved_blocks = await cli_utils.async_parse_block_slice(blocks)
        if verbose:
            import asyncio
            from ctc.protocols import chainlink_utils

            eth_usd_coroutine = chainlink_utils.async_get_feed_data(
                'ETH_USD',
                blocks=resolved_blocks,
            )
            eth_usd_task = asyncio.create_task(eth_usd_coroutine)

        wallet = wallets[0]
        wallet = await evm.async_resolve_address(wallet, block=blocks[-1])
        balances = await evm.async_get_eth_balance_by_block(
            address=wallet,
            blocks=resolved_blocks,
            normalize=(not raw),
        )

        styles = cli.get_cli_styles()

        toolstr.print_text_box(
            'ETH Balances for ' + wallet, style=styles['title']
        )
        print()

        if verbose:
            eth_usd = (await eth_usd_task).values
            usd_balances = [
                balance * eth_price
                for balance, eth_price in zip(balances, eth_usd)
            ]
        rows = []
        for b in range(len(resolved_blocks)):
            row = [
                resolved_blocks[b],
                balances[b],
            ]
            if verbose:
                row.append(usd_balances[b])
                row.append(eth_usd[b])
            rows.append(row)

        labels = ['block', 'balance']
        if verbose:
            labels.append('$ balance')
            labels.append('ETH price')

        toolstr.print_table(
            rows=rows,
            labels=labels,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'block': styles['metavar'],
                'balance': styles['description'],
                '$ balance': styles['description'],
                'ETH price': styles['description'],
            },
            column_formats={
                '$ balance': {
                    'prefix': '$',
                    'trailing_zeros': True,
                    'order_of_magnitude': True,
                },
                'ETH price': {'prefix': '$', 'trailing_zeros': True},
            },
            indent=4,
        )

        def formatter(xval: typing.Any) -> str:
            return toolstr.format(round(xval))

        xvals = resolved_blocks
        yvals = balances
        plot = toolstr.render_line_plot(
            xvals=xvals,
            yvals=yvals,
            n_rows=40,
            n_columns=120,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            xaxis_kwargs={'formatter': formatter},
        )
        print()
        print()
        toolstr.print(
            toolstr.hjustify('ETH balance over time', 'center', 70),
            indent=4,
            style=styles['title'],
        )
        toolstr.print(plot, indent=4)

        if verbose:
            xvals = resolved_blocks
            yvals = usd_balances
            plot = toolstr.render_line_plot(
                xvals=xvals,
                yvals=yvals,
                n_rows=40,
                n_columns=120,
                line_style=styles['description'],
                chrome_style=styles['comment'],
                tick_label_style=styles['metavar'],
                xaxis_kwargs={'formatter': formatter},
                yaxis_kwargs={'tick_label_format': {'prefix': '$'}},
            )
            print()
            print()
            toolstr.print(
                toolstr.hjustify('ETH balance over time (USD)', 'center', 70),
                indent=4,
                style=styles['title'],
            )
            toolstr.print(plot, indent=4)

        if export != 'stdout':
            df = pd.DataFrame(balances, index=resolved_blocks)
            df.index.name = 'block'
            df.columns = ['balance']
            output_data: typing.Union[spec.DataFrame, spec.Series] = df
            cli_utils.output_data(
                output_data, export, overwrite=overwrite, indent=indent, raw=raw
            )
    else:
        # multiple wallets, single block
        if blocks is not None:
            raise Exception(
                'cannot specify multiple wallets and multiple blocks'
            )

        if block is None:
            block = 'latest'
        block = await evm.async_block_number_to_int(block)

        if wallets is not None:
            wallets = await evm.async_resolve_addresses(wallets, block=block)
            balances = await evm.async_get_eth_balance_of_addresses(
                addresses=wallets,
                block=block,
                normalize=(not raw),
            )

            series = pd.Series(balances, index=wallets)
            series.name = 'balance'
            series.index.name = 'address'
            output_data = series

        cli_utils.output_data(
            output_data, export, overwrite=overwrite, indent=indent, raw=raw
        )
