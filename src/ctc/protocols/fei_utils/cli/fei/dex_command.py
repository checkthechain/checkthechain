from __future__ import annotations

import toolcli
import toolstr

from ctc import evm
from ctc import spec
from ctc.protocols.fei_utils import fei_dexes


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_dexes_command,
        'help': 'show information related to FEI on DEX\'s',
        'args': [
            {'name': '--block', 'help': 'block number to query'},
        ],
        'examples': [
            '',
            '--block 14000000',
        ],
    }


async def async_dexes_command(block: spec.BlockNumberReference | None) -> None:
    import asyncio

    if block is None:
        block = 'latest'
    blocks = [block]

    # get block number concurrently
    if block == 'latest':
        block_task = asyncio.create_task(evm.async_get_latest_block_number())

    metrics = await fei_dexes.async_get_fei_stable_dex_metrics_by_block(
        blocks=blocks,
    )

    if block == 'latest':
        block = await block_task

    print_dex_table(metrics, block=block)


def print_dex_table(
    metrics: fei_dexes.FEIDEXMetrics,
    block: spec.BlockNumberReference,
) -> None:

    labels = [
        'Pool',
        'Total TVL',
        'FEI TVL',
        'FEI Imbalance',
    ]

    rows = []
    for pool_name in metrics['pool_tvls'].keys():
        tvl = metrics['pool_tvls'][pool_name][-1]
        fei_balance = metrics['pool_balances'][pool_name + '__FEI'][-1]
        imbalance = metrics['pool_imbalances'][pool_name][-1]

        row = [
            pool_name,
            tvl,
            fei_balance,
            imbalance,
        ]

        rows.append(row)

    row = [''] * 4
    rows.append(row)

    row = [
        'TOTAL',
        metrics['total_tvl'][-1],
        metrics['total_FEI'][-1],
        metrics['total_imbalance'][-1],
    ]
    rows.append(row)

    toolstr.print_text_box('Fei Stableswaps')
    print('(block = ' + str(block) + ')')
    print()
    format = {'trailing_zeros': 2, 'decimals': 2, 'order_of_magnitude': True}
    toolstr.print_table(
        rows,
        labels=labels,
        format=format,
        column_formats={'Total TVL': dict(format, prefix='$')},
    )
