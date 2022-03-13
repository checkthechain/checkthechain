import os

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_address_command,
        'help': 'summarize address',
        'args': [
            {'name': 'address', 'help': 'address to get summary of'},
            {
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'emit extra output',
            },
            {
                'name': '--network',
                'metavar': 'NAME_OR_ID',
                'help': 'network name or id to scan address of',
            },
        ],
    }


async def async_address_command(address, verbose, network, **kwargs):
    try:
        max_width = os.get_terminal_size().columns
    except OSError:
        max_width = 80

    if verbose:
        verbose = 2
    await evm.async_print_address_summary(
        address=address,
        verbose=verbose,
        max_width=max_width,
        provider={'network': network},
    )
    await rpc.async_close_http_session()

