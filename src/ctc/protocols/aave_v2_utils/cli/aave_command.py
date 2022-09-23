from __future__ import annotations

import asyncio
import typing

import toolcli
import tooltime

from ctc import evm
from ctc import spec
from ctc.protocols import aave_v2_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_aave_command,
        'help': 'output aave usage statistics',
        'args': [
            {
                'name': 'token',
                'help': 'show information related to this token',
                'nargs': '?',
            },
            {
                'name': ['--verbose', '-v'],
                'help': 'show additional addresses',
                'action': 'store_true',
            },
            {
                'name': '--block',
                'help': 'block to get addresses of',
            },
            {
                'name': '--time',
                'help': 'timescale to use for token-specific charts',
            },
            {
                'name': '-n',
                'help': 'number of blocks to sample',
                'default': 40,
                'type': int,
            },
        ],
        'examples': [
            '',
            '--verbose',
            '--block 14000000',
            'DAI',
            'DAI --time 1y -n 10',
            'DAI --time 1y --verbose -n 10',
        ],
    }


async def async_aave_command(
    *,
    token: str | None,
    verbose: bool,
    block: str | None,
    time: str | None,
    n: int | None,
) -> None:

    if block is None:
        block = 'latest'
    block_reference = evm.standardize_block_number(block)

    if token is not None:

        blocks = await _async_sample_blocks(
            timelength=time,
            n_samples=n,
            end_block=block_reference,
        )

        await aave_v2_utils.async_print_token_market_summary(
            token=token,
            verbose=verbose,
            blocks=blocks,
        )

    else:
        await aave_v2_utils.async_print_token_markets_summary(
            verbose=verbose,
            block=block,
        )


async def _async_sample_blocks(
    *,
    n_samples: int | None,
    timelength: tooltime.Timelength | None = None,
    end_block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:

    import time
    import numpy as np

    if n_samples is None:
        n_samples = 100

    if timelength is None:
        timelength = '30d'

    if end_block is None or end_block == 'latest':
        end_block_task = asyncio.create_task(
            evm.async_get_latest_block_number()
        )

    # compute timelength
    end_time = int(time.time())
    start_time = end_time - tooltime.timelength_to_seconds(timelength)
    start_block = await evm.async_get_block_of_timestamp(
        start_time,
        mode='<=',
    )

    if end_block is None or end_block == 'latest':
        end_block = await end_block_task
    if not isinstance(end_block, int):
        raise Exception('invalid type for end_block')

    samples = np.linspace(start_block, end_block, n_samples).astype(int)

    return samples  # type: ignore
