from ctc import evm
from ctc import rpc
from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': async_owner_command,
        'help': 'output owner of ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
            {'name': '--block', 'help': 'block number'},
        ],
    }


async def async_owner_command(name, block):
    if block is not None:
        block = evm.standardize_block_number(block)
    owner = await ens_utils.async_get_owner(name, block=block)
    print(owner)
    await rpc.async_close_http_session()

