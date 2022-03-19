from __future__ import annotations

import typing

import toolcli

from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_transfers_command,
        'help': 'output information about ERC20 transfers',
        'args': [
            {'name': 'erc20', 'help': 'ERC20 address'},
            {
                'name': '--blocks',
                'nargs': '+',
                'help': 'block range of transfers',
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


async def async_transfers_command(
    erc20: str, blocks: list[str], output: typing.Optional[str], overwrite: bool
) -> None:

    if blocks is not None:
        start_block, end_block = await cli_utils.async_resolve_block_range(
            blocks
        )
    else:
        start_block = None
        end_block = None

    transfers = await evm.async_get_erc20_transfers(
        erc20,
        start_block=start_block,
        end_block=end_block,
    )
    cli_utils.output_data(transfers, output=output, overwrite=overwrite)
    await rpc.async_close_http_session()

