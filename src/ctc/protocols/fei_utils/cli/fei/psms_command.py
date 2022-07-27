from __future__ import annotations

import toolcli
import tooltime
import toolstr

from ctc.protocols.fei_utils import fei_psms
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_psms_command,
        'help': 'display recent FEI redemptions',
        'args': [
            {
                'name': '--time',
                'help': 'span of time to display',
                'default': '24h',
            },
            {
                'name': '--token',
                'help': 'filter by redemptions of a particular token',
            },
            {
                'name': '--block',
                'help': 'block',
                'default': 'latest',
            },
            {
                'name': '--limit',
                'help': 'limit number of mints/redeems shown',
                'type': int,
                'default': 15,
            },
            {
                'name': ['--verbose', '-v'],
                'help': 'display additional information',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            '--verbose',
        ],
    }


async def async_psms_command(
    *,
    time: tooltime.Timelength,
    token: str,
    block: spec.BlockNumberReference,
    limit: int,
    verbose: bool,
) -> None:
    import asyncio

    mints_task = asyncio.create_task(
        fei_psms.async_get_fei_psm_mints(start_block=14700000)
    )
    redeems_task = asyncio.create_task(
        fei_psms.async_get_fei_psm_redemptions(start_block=14700000)
    )

    await async_print_psm_state(block=block)

    # print recent redemptions
    print()
    print()
    mints = await mints_task
    fei_psms.print_fei_psm_mints(mints, limit=limit, verbose=verbose)
    print()
    print()
    redemptions = await redeems_task
    fei_psms.print_fei_psm_redemptions(
        redemptions, limit=limit, verbose=verbose
    )


async def async_print_psm_state(block: spec.BlockNumberReference) -> None:
    import asyncio

    psms = fei_psms.get_psms()

    mint_paused_coroutines = [
        rpc.async_eth_call(
            to_address=psm_address,
            function_name='paused',
            block_number=block,
        )
        for psm_name, psm_address in psms.items()
    ]
    redeem_paused_coroutines = [
        rpc.async_eth_call(
            to_address=psm_address,
            function_name='redeemPaused',
            block_number=block,
        )
        for psm_name, psm_address in psms.items()
    ]
    mint_paused_tasks = [
        asyncio.create_task(mint_coroutine)
        for mint_coroutine in mint_paused_coroutines
    ]
    redeem_paused_tasks = [
        asyncio.create_task(redeem_coroutine)
        for redeem_coroutine in redeem_paused_coroutines
    ]
    mint_paused = await asyncio.gather(*mint_paused_tasks)
    redeem_paused = await asyncio.gather(*redeem_paused_tasks)

    # print PSM state
    toolstr.print_text_box('FEI PSMs')
    print('(block = ' + str(block) + ')')
    print()
    labels = [
        'PSM',
        'minting',
        'redeeming',
        'address',
    ]
    rows = []
    for p, (psm_name, psm_address) in enumerate(psms.items()):
        row = [
            ' '.join(psm_name.split(' ')[:-1]),
            str(not bool(mint_paused[p])),
            str(not bool(redeem_paused[p])),
            psm_address,
        ]
        rows.append(row)
    toolstr.print_table(rows=rows, labels=labels)
