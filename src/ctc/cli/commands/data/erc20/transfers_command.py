from __future__ import annotations

import typing

import toolcli

from ctc import evm
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
                'name': '--include_timestamps',
                'default': False,
                'action': 'store_true',
                'help': 'include timestamps',
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
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca': {'long': True},
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --blocks [14000000, 14001000]': {},
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca --blocks [14000000, 14001000] --include_timestamps': {},
        },
    }


async def async_transfers_command(
    *,
    erc20: str,
    blocks: typing.Sequence[str],
    include_timestamps: bool,
    output: str,
    overwrite: bool,
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
        include_timestamps=include_timestamps,
    )

    if output == 'stdout' and include_timestamps:
        transfers = transfers.astype({'timestamp': 'str'})
    cli_utils.output_data(transfers, output=output, overwrite=overwrite)
