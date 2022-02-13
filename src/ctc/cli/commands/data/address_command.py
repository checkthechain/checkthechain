import os

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_address_command,
        'args': [
            {'name': 'address'},
            {'name': ['-v', '--verbose'], 'kwargs': {'action': 'store_true'}},
        ],
    }


async def async_address_command(address, verbose, **kwargs):
    max_width = os.get_terminal_size().columns
    if verbose:
        verbose = 2
    await evm.async_print_address_summary(
        address=address, verbose=verbose, max_width=max_width
    )
    await rpc.async_close_http_session()

