from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc.protocols import uniswap_v2_utils
from ctc.toolbox.defi_utils.dex_utils.amm_utils import cpmm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_pool_command,
        'help': 'summarize pool',
        'args': [
            {'name': 'pool', 'help': 'pool address'},
            {
                'name': '--block',
                'default': 'latest',
                'help': 'block number range',
            },
            {'name': '--depths', 'help': 'liquidity depths', 'nargs': '+'},
        ],
        'examples': [
            '0xae461ca67b15dc8dc81ce7615e0320da1a9ab8d5 --block 14000000',
        ],
    }


async def async_pool_command(
    *,
    pool: spec.Address,
    block: str,
    depths: typing.Sequence[str] | None,
) -> None:
    tokens_metadata = await uniswap_v2_utils.async_get_pool_tokens_metadata(
        pool
    )
    x_symbol = tokens_metadata['x_symbol']
    y_symbol = tokens_metadata['y_symbol']
    title = 'Uniswap V2 Pool: ' + x_symbol + ' x ' + y_symbol
    toolstr.print_text_box(title)
    print('-', x_symbol, 'address:', tokens_metadata['x_address'])
    print('-', y_symbol, 'address:', tokens_metadata['y_address'])
    print('-', x_symbol, 'decimals:', tokens_metadata['x_decimals'])
    print('-', y_symbol, 'decimals:', tokens_metadata['y_decimals'])
    print()
    print()

    if depths is not None:
        depths_float: list[float] | None = [float(depth) for depth in depths]
    else:
        depths_float = None

    toolstr.print_header('Pool State')
    pool_state = await uniswap_v2_utils.async_get_pool_state(pool, block=block)
    cpmm.print_pool_summary(
        x_name=x_symbol,
        y_name=y_symbol,
        depths=depths_float,
        **pool_state,
    )
