from __future__ import annotations

import typing

import toolcli
import tooltime

from ctc import binary
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
        ],
        'examples': [
            '',
            '--verbose',
            '--block 14000000',
            'DAI',
            'DAI --time 1y',
            'DAI --time 1y --verbose',
        ],
    }


async def async_aave_command(
    *,
    token: str | None,
    verbose: bool,
    block: str | None,
    time: str | None,
) -> None:

    if block is None:
        block = 'latest'
    block_reference = binary.standardize_block_number(block)

    if token is not None:

        blocks = await _async_sample_blocks(timelength=time, end_block=block_reference)

        await aave_v2_utils.async_summarize_token_market(
            token=token,
            verbose=verbose,
            blocks=blocks,
        )

    else:
        await aave_v2_utils.async_summarize_token_markets(
            verbose=verbose,
            block=block,
        )


async def _async_sample_blocks(
    *,
    timelength: tooltime.Timelength | None = None,
    n_samples: int = 100,
    end_block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:

    import time
    import numpy as np

    if timelength is None:
        timelength = '30d'

    # compute timelength
    end_time = int(time.time())
    start_time = end_time - tooltime.timelength_to_seconds(timelength)
    start_block, end_block = await evm.async_get_blocks_of_timestamps(
        [start_time, end_time],
        mode='<=',
    )

    n_samples = 100
    samples = np.linspace(start_block, end_block, n_samples).astype(int)

    return samples  # type: ignore
