"""
# balances of wallets within single block
ctc eth balances <wallets> [--block <block>]

# balance of single wallet across multiple blocks
ctc eth balances <wallet> [--blocks <block>]
"""

import pandas as pd

from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec():
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
                'name': '--output',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
        ],
    }


async def async_balances_command(
    wallets,
    block,
    blocks,
    raw,
    output,
    overwrite,
):
    indent = None
    wallets = [wallet.lower() for wallet in wallets]

    if blocks is not None:
        # single wallet, multiple blocks
        if len(wallets) > 1:
            raise Exception(
                'cannot specify multiple wallets and multiple blocks'
            )

        wallet = wallets[0]
        resolved_blocks = await cli_utils.async_resolve_blocks(blocks)
        balances = await evm.async_get_eth_balance_by_block(
            address=wallet,
            blocks=resolved_blocks,
            normalize=(not raw),
        )
        df = pd.DataFrame(balances, index=resolved_blocks)
        df.index.name = 'block'
        df.columns = ['balance']

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
            balances = await evm.async_get_eth_balance_of_addresses(
                addresses=wallets,
                block=block,
                normalize=(not raw),
            )

            df = pd.Series(balances, index=wallets)
            df.name = 'balance'
            df.index.name = 'address'

    cli_utils.output_data(df, output, overwrite, indent=indent, raw=raw)

    await rpc.async_close_http_session()

