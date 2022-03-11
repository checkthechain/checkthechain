from ctc.protocols import ens_utils
from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_exists_command,
        'help': 'output whether ENS name exists',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
            {'name': '--block', 'help': 'block number'},
        ],
    }


async def async_exists_command(name, block):

    if block is not None:
        block = evm.standardize_block_number(block)
    exists = await ens_utils.async_record_exists(name, block=block)

    print(exists)
    await rpc.async_close_http_session()

