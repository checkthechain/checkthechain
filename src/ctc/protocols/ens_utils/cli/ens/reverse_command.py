from ctc import evm
from ctc import rpc
from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': async_reverse_command,
        'help': 'reverse ENS lookup address',
        'args': [
            {'name': 'address', 'help': 'address of reverse lookup'},
            {'name': '--block', 'help': 'block number'},
        ]
    }


async def async_reverse_command(address, block):
    if block is not None:
        block = evm.standardize_block_number(block)
    name = await ens_utils.async_reverse_lookup(address, block=block)
    print(name)
    await rpc.async_close_http_session()

