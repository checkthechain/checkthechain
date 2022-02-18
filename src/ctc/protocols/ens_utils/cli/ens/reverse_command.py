from ctc import evm
from ctc import rpc
from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': async_reverse_command,
        'args': [
            {'name': 'name'},
            {'name': '--block'},
        ]
    }


async def async_reverse_command(name, block):
    if block is not None:
        block = evm.standardize_block_number(block)
    address = await ens_utils.async_reverse_lookup(name, block=block)
    print(address)
    await rpc.async_close_http_session()

