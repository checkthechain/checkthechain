"""
# balances of wallets within single block
ctc eth balances <wallets> [--block <block>]

# balance of single wallet across multiple blocks
ctc eth balances <wallet> [--blocks <block>]
"""

from __future__ import annotations

import typing

import toolcli

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
        'examples': {
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 0xea674fdde714fd979de3edf0f56aa9716b898ec8 0xbe0eb53f46cd790cd13851d5eff43d12404d33e8': 'multiple wallets',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 --blocks [14000000, 14000100]': 'multiple blocks',
        },
    }


async def async_balances_command(
    *,
    wallets: typing.Sequence[str],
    block: typing.Optional[spec.BlockNumberReference],
    blocks: typing.Optional[typing.Sequence[str]],
    raw: bool,
    output: str,
    overwrite: bool,
) -> None:
    import pandas as pd

    indent = None
    wallets = [wallet.lower() for wallet in wallets]

    if blocks is not None:
        # single wallet, multiple blocks
        if len(wallets) > 1:
            raise Exception(
                'cannot specify multiple wallets and multiple blocks'
            )

        wallet = wallets[0]
        wallet = await evm.async_resolve_address(wallet, block=blocks[-1])
        resolved_blocks = await cli_utils.async_resolve_block_range(blocks)
        balances = await evm.async_get_eth_balance_by_block(
            address=wallet,
            blocks=resolved_blocks,
            normalize=(not raw),
        )
        df = pd.DataFrame(balances, index=resolved_blocks)
        df.index.name = 'block'
        df.columns = ['balance']
        output_data: typing.Union[spec.DataFrame, spec.Series] = df

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
        output_data, output, overwrite=overwrite, indent=indent, raw=raw
    )
