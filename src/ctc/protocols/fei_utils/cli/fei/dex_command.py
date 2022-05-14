from __future__ import annotations

import asyncio

import toolcli
import tooltable  # type: ignore
import toolstr

from ctc import evm
from ctc import spec
from ctc import rpc
from ctc.protocols.fei_utils import fei_dexes


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_dexes_command,
        'help': 'show information related to FEI on DEX\'s',
        'args': [
            {'name': '--block', 'help': 'block number to query'},
        ],
    }


async def async_dexes_command(block: spec.BlockNumberReference | None) -> None:
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
    await rpc.async_close_http_session()


def print_dex_table(
    metrics: fei_dexes.FEIDEXMetrics,
    block: spec.BlockNumberReference,
) -> None:

    headers = [
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
            toolstr.format(tvl, order_of_magnitude=True, prefix='$'),
            toolstr.format(fei_balance, order_of_magnitude=True),
            toolstr.format(imbalance, order_of_magnitude=True),
        ]

        rows.append(row)

    row = [''] * 4
    rows.append(row)

    row = [
        'TOTAL',
        toolstr.format(
            metrics['total_tvl'][-1], order_of_magnitude=True, prefix='$'
        ),
        toolstr.format(metrics['total_FEI'][-1], order_of_magnitude=True),
        toolstr.format(metrics['total_imbalance'][-1], order_of_magnitude=True),
    ]
    rows.append(row)

    toolstr.print_text_box('Fei Stable DEX State')
    print('(block = ' + str(block) + ')')
    print()
    tooltable.print_table(rows, headers=headers)
