from ctc import evm
from ctc import rpc
from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': async_resolve_command,
        'args': [
            {'name': 'name'},
            {'name': '--block'},
        ]
    }


async def async_resolve_command(name, block):
    if block is not None:
        block = evm.standardize_block_number(block)
    address = await ens_utils.async_resolve_name(name, block=block)
    print(address)
    await rpc.async_close_http_session()

