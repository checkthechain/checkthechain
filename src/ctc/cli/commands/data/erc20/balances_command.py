"""
# balance of single wallet across multiple tokens;
ctc erc20 balances <wallet> --erc20s <erc20s> [--block <block>]

# balances of wallets within single block (default = all wallets)
ctc erc20 balances <erc20> [--block <block>] [--wallets <wallets>]

# balance of single wallet across multiple blocks
ctc erc20 balances <erc20> <wallet> --blocks <blocks>
"""

import pandas as pd

import toolstr

from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec():
    return {
        'f': async_balances_command,
        'args': [
            {'name': 'args', 'kwargs': {'nargs': '+'}},
            {'name': '--block'},
            {'name': '--wallets', 'kwargs': {'nargs': '+'}},
            {'name': '--blocks', 'kwargs': {'nargs': '+'}},
            {'name': '--erc20s', 'kwargs': {'nargs': '+'}},
            #
            {'name': '--raw', 'kwargs': {'action': 'store_true'}},
            {'name': '--output', 'kwargs': {'default': 'stdout'}},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
            {'name': '--top'},
        ],
    }


async def async_balances_command(
    args, block, wallets, blocks, erc20s, raw, output, overwrite, top
):
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

            df = pd.Series(balances, index=wallets)
            df.name = 'balance'
            df.index.name = 'address'

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
            symbol = await symbol_coroutine

            if top is None:
                top = 20

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

        resolved_blocks = await cli_utils.async_resolve_blocks(blocks)
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

    else:
        raise Exception('invalid inputs')

    cli_utils.output_data(df, output, overwrite, top=top, indent=indent)

    await rpc.async_close_http_session()

