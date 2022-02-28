from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec():
    return {
        'f': async_transfers_command,
        'help': 'output information about ERC20 transfers',
        'args': [
            {'name': 'erc20'},
            {'name': '--blocks', 'nargs': '+'},
            {'name': '--output', 'default': 'stdout'},
            {'name': '--overwrite', 'action': 'store_true'},
        ],
    }


async def async_transfers_command(erc20, blocks, output, overwrite):

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
    )
    cli_utils.output_data(transfers, output=output, overwrite=overwrite)
    await rpc.async_close_http_session()

