from __future__ import annotations

import typing

import pandas as pd
import toolcli
import toolstr

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.cli import cli_utils


command_help = """output ERC20 balances of blocks / addresses / tokens

[comment]# example: balance of single wallet across multiple tokens[/comment]
[option]ctc erc20 balances WALLET --erc20s ERC20S [--block BLOCK][/option]

[comment]# example: balances of wallets within single block (default = all wallets)[/comment]
[option]ctc erc20 balances ERC20 [--block BLOCK] [--wallets WALLETS][/option]

[comment]# example: balance of single wallet across multiple blocks[/comment]
[option]ctc erc20 balances ERC20 WALLET --blocks BLOCKS[/option]"""


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
                'name': '--output',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {'name': '--top', 'metavar': 'N', 'help': 'show top N addresses'},
        ],
    }


async def async_balances_command(
    args: list[str],
    block: typing.Optional[spec.BlockNumberReference],
    wallets: typing.Optional[list[str]],
    blocks: typing.Optional[list[str]],
    erc20s: typing.Optional[list[str]],
    raw: bool,
    output: typing.Optional[str],
    overwrite: bool,
    top: typing.Optional[str],
) -> None:
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
        symbols_coroutine = evm.async_get_erc20s_symbols(erc20s)
        balances = await evm.async_get_erc20s_balance_of(
            address=wallet,
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
        symbol_coroutine = evm.async_get_erc20_symbol(erc20)

        if wallets is not None:
            balances = await evm.async_get_erc20_balance_of_addresses(
                addresses=wallets,
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
            transfers = await evm.async_get_erc20_transfers(
                erc20,
                start_block=None,
                end_block=block,
                normalize=False,
            )
            df = await evm.async_get_erc20_holdings_from_transfers(
                transfers=transfers, dtype=None, normalize=(not raw)
            )
            output_data = df
            symbol = await symbol_coroutine

            if top is None:
                top = '20'

            print()
            toolstr.print_text_box(symbol + ' Balances')
            print('- token:', erc20)
            print('- symbol:', symbol)
            print('- block:', block)
            print()
            print()
            toolstr.print_header('Showing Top ' + str(top) + ' Holders')
            print()
            indent = '    '

    elif len(args) == 2 and blocks is not None:
        # single erc20, single address, multiple blocks
        if erc20s is not None or wallets is not None:
            raise Exception(
                'can only specify one of --erc20s --wallets, --blocks'
            )
        erc20, wallet = args

        resolved_blocks = await cli_utils.async_resolve_block_range(blocks)
        balances = await evm.async_get_erc20_balance_of_by_block(
            address=wallet,
            token=erc20,
            blocks=resolved_blocks,
            normalize=(not raw),
            empty_token=0,
        )
        df = pd.DataFrame(balances, index=resolved_blocks)
        df.index.name = 'block'
        df.columns = ['balance']
        output_data = df

    else:
        raise Exception('invalid inputs')

    cli_utils.output_data(
        output_data, output, overwrite, top=top, indent=indent
    )

    await rpc.async_close_http_session()

