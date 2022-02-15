"""

information:
- pool metadata
- pool state
"""
import toolstr

from ctc.protocols import uniswap_v2_utils
from ctc.toolbox.amm_utils import cpmm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_pool_command,
        'args': [
            {'name': 'pool'},
            {'name': '--block', 'kwargs': {'default': 'latest'}},
        ],
    }


async def async_pool_command(pool, block):
    tokens_metadata = await uniswap_v2_utils.async_get_pool_tokens_metadata(pool)
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

    toolstr.print_header('Pool State')
    pool_state = await uniswap_v2_utils.async_get_pool_state(pool, block=block)
    cpmm.print_pool_summary(
        x_name=x_symbol,
        y_name=y_symbol,
        **pool_state,
    )

    await rpc.async_close_http_session()

