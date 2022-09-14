from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import spec
from ctc.cli import cli_utils


command_help = """output ERC20 balances of blocks / addresses / tokens"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_balances_command,
        'help': command_help,
        'args': [
            {'name': 'args', 'nargs': '+', 'help': '<see above>'},
            {'name': '--block', 'help': 'block number'},
            {
                'name': '--wallets',
                'nargs': '+',
                'help': 'wallets to get balances of',
            },
            {
                'name': '--blocks',
                'nargs': '+',
                'help': 'block numbers to get balances at',
            },
            {
                'name': '--erc20s',
                'nargs': '+',
                'help': 'ERC20 addresses to get balances of',
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
            'WALLET --erc20s ERC20S [--block BLOCK]': {
                'description': 'version 1: balance of single wallet across multiple tokens',
                'runnable': False,
            },
            'ERC20 [--block BLOCK] [--wallets WALLETS]': {
                'description': 'version 2: balances of multiple wallets in single block (default = all wallets)',
                'runnable': False,
            },
            'ERC20 WALLET --blocks BLOCKS': {
                'description': 'version 3: balance of single wallet across multiple blocks',
                'runnable': False,
            },
        },
    }


async def async_balances_command(
    *,
    args: typing.Sequence[str],
    block: typing.Optional[spec.BlockNumberReference],
    wallets: typing.Optional[typing.Sequence[str]],
    blocks: typing.Optional[typing.Sequence[str]],
    erc20s: typing.Optional[typing.Sequence[str]],
    raw: bool,
    export: str,
    overwrite: bool,
    n: int | None,
) -> None:

    import pandas as pd

    if wallets is not None:
        wallets = await evm.async_resolve_addresses(wallets, block=block)
    if erc20s is not None:
        erc20s = await evm.async_resolve_addresses(erc20s, block=block)

    indent = None

    if len(args) == 1 and erc20s is not None:
        # multiple erc20s, single wallet, single block
        if wallets is not None or blocks is not None:
            raise Exception(
                'can only specify one of --erc20s --wallets, --blocks'
            )
        wallet = args[0]

        if block is None:
            block = 'latest'
        block = await evm.async_block_number_to_int(block)
        wallet = await evm.async_resolve_address(wallet, block=block)
        symbols_coroutine = evm.async_get_erc20s_symbols(erc20s)
        balances = await evm.async_get_erc20s_balances(
            wallet=wallet,
            tokens=erc20s,
            block=block,
            normalize=(not raw),
        )
        symbols = await symbols_coroutine
        data = {'balance': balances, 'symbol': symbols, 'erc20_address': erc20s}
        df = pd.DataFrame(data)
        df = df.set_index('erc20_address')
        output_data: typing.Union[spec.DataFrame, spec.Series] = df

        toolstr.print_text_box('ERC20 balances in wallet')
        print('- wallet:', wallet)
        print('- block:', block)
        print('- n_tokens:', len(erc20s))
        print()
        print()
        indent = '    '

    elif len(args) == 1:
        # single erc20, multiple wallets, single block
        if blocks is not None or erc20s is not None:
            raise Exception(
                'can only specify one of --erc20s --wallets, --blocks'
            )
        erc20 = args[0]

        if block is None:
            block = 'latest'
        block = await evm.async_block_number_to_int(block)
        erc20 = await evm.async_resolve_address(erc20, block=block)
        symbol_coroutine = evm.async_get_erc20_symbol(erc20)

        if wallets is not None:
            balances = await evm.async_get_erc20_balances_of_addresses(
                wallets=wallets,
                token=erc20,
                block=block,
                normalize=(not raw),
            )
            symbol = await symbol_coroutine

            series = pd.Series(balances, index=wallets)
            series.name = 'balance'
            series.index.name = 'address'
            output_data = series

            print()
            toolstr.print_text_box(symbol + ' Balances')
            print('- token:', erc20)
            print('- symbol:', symbol)
            print('- block:', block)
            print()
            print()

        else:

            import eth_abi_lite

            try:
                symbol = await symbol_coroutine
            except eth_abi_lite.exceptions.InsufficientDataBytes:
                print(
                    'this is an EOA, see `ctc erc20 balances -h` for proper syntax'
                )
                return

            transfers = await evm.async_get_erc20_transfers(
                erc20,
                start_block=None,
                end_block=block,
                normalize=False,
            )
            df = await evm.async_get_erc20_balances_from_transfers(
                transfers=transfers, dtype=None, normalize=(not raw)
            )
            output_data = df

            if n is None:
                n = 20

            print()
            toolstr.print_text_box(symbol + ' Balances')
            print('- token:', erc20)
            print('- symbol:', symbol)
            print('- block:', block)
            print()
            print()
            toolstr.print_header('Showing Top ' + str(n) + ' Holders')
            print()
            indent = '    '

    elif len(args) == 2 and blocks is not None:
        # single erc20, single address, multiple blocks
        if erc20s is not None or wallets is not None:
            raise Exception(
                'can only specify one of --erc20s --wallets, --blocks'
            )
        erc20, wallet = args
        resolved_blocks = await cli_utils.async_parse_block_slice(blocks, n=n)

        timestamps = await evm.async_get_block_timestamps(resolved_blocks)

        erc20 = await evm.async_resolve_address(
            erc20, block=resolved_blocks[-1]
        )
        wallet = await evm.async_resolve_address(
            wallet, block=resolved_blocks[-1]
        )
        balances = await evm.async_get_erc20_balance_by_block(
            wallet=wallet,
            token=erc20,
            blocks=resolved_blocks,
            normalize=(not raw),
            empty_token=0,
        )

        if export == 'stdout':
            styles = cli.get_cli_styles()

            # print header
            toolstr.print_text_box(
                'Historical ERC20 Balances', style=styles['title']
            )
            print()
            toolstr.print_table(
                rows=[['token', erc20], ['wallet', wallet]],
                column_justify=['right', 'left'],
                border=styles['comment'],
                column_styles=[styles['option'], styles['metavar']],
            )

            import tooltime

            # print balance history table
            print()
            print()
            rows = []
            for block, timestamp, balance in zip(resolved_blocks, timestamps, balances):
                age = tooltime.get_age(timestamp, 'TimelengthPhrase')
                age = ', '.join(age.split(', ')[:1])
                row = [tooltime.timestamp_to_iso(timestamp), age, block, balance]
                rows.append(row)
            labels = ['timestamp', 'age', 'block', 'balance']
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

            return

        else:
            df = pd.dataframe(balances, index=resolved_blocks)
            df.index.name = 'block'
            df.columns = ['balance']
            output_data = df

    else:
        raise Exception('invalid inputs')

    cli_utils.output_data(
        output_data,
        output=export,
        overwrite=overwrite,
        top=n,
        indent=indent,
    )
