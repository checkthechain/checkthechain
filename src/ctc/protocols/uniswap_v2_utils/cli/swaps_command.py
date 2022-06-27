from __future__ import annotations

import typing

import toolcli

from ctc.protocols import uniswap_v2_utils
from ctc.cli import cli_utils
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_swaps_command,
        'help': 'output information about pool swaps',
        'args': [
            {'name': 'pool', 'help': 'pool address'},
            {'name': '--blocks', 'nargs': '+', 'help': 'block number range'},
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


async def async_swaps_command(
    *,
    pool: spec.Address,
    blocks: typing.Sequence[str],
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

    swaps = await uniswap_v2_utils.async_get_pool_swaps(
        pool,
        replace_symbols=True,
        start_block=start_block,
        end_block=end_block,
    )
    cli_utils.output_data(swaps, output, overwrite=overwrite)
