from __future__ import annotations

import toolcli
import toolstr
import typing

from ctc import evm
from ctc import spec
from ctc.protocols import fei_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_pcv_command,
        'help': 'output summary of Fei PCV',
        'args': [
            {'name': '--block', 'help': 'block number'},
        ],
        'examples': [
            '',
            '--block 14000000',
        ],
    }


async def async_pcv_command(
    block: typing.Optional[spec.BlockNumberReference],
) -> None:

    if block is not None:
        block = await evm.async_block_number_to_int(block)

    pcv_stats = await fei_utils.async_get_pcv_stats(block=block)
    FEI = '0x956f47f50a910163d8bf957cf5846d573e7f87ca'
    total_fei = await evm.async_get_erc20_total_supply(FEI, block=block)

    total_pcv = pcv_stats['pcv'] / 1e18
    user_fei = pcv_stats['user_fei'] / 1e18
    protocol_fei = total_fei - user_fei
    protocol_equity = total_pcv - user_fei
    cr = total_pcv / user_fei

    # output = 'list'
    output = 'table'

    format_kwargs: toolstr.NumberFormat = {
        'order_of_magnitude': True,
        'prefix': '$',
        'oom_blank': ' ',
        'trailing_zeros': True,
    }
    if output == 'list':
        toolstr.print_text_box('Fei PCV Summary')
        print('- total PCV:', toolstr.format(total_pcv, **format_kwargs))
        print('- total FEI:', toolstr.format(total_fei, **format_kwargs))
        print('- user FEI:', toolstr.format(user_fei, **format_kwargs))
        print('- protocol FEI:', toolstr.format(protocol_fei, **format_kwargs))
        print('- PCV equity:', toolstr.format(protocol_equity, **format_kwargs))
        print('- CR:', toolstr.format(cr, percentage=True))
    elif output == 'table':
        rows = [
            ['total PCV', total_pcv],
            ['total FEI', total_fei],
            ['user FEI', user_fei],
            ['protocol FEI', protocol_fei],
            ['PCV equity', protocol_equity],
            ['CR', cr],
        ]
        toolstr.print_text_box('Fei PCV Summary')
        toolstr.print_table(
            rows,
            labels=['', 'amount'],
            format=format_kwargs,
            column_formats={'CR': {'percentage': True}},
        )
