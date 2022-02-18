from ctc import evm
from ctc import rpc

from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': ens_command,
        'args': [
            {'name': 'args', 'kwargs': {'nargs': '+'}},
            {'name': '--block'},
        ],
    }


async def ens_command(args, block):
    if len(args) == 1:
        arg = args[0]

        if block is not None:
            block = evm.standardize_block_number(block)

        if '.' in arg:
            output = await ens_utils.async_resolve_name(arg, block=block)
        elif evm.is_address_str(arg):
            output = await ens_utils.async_reverse_lookup(arg, block=block)
        else:
            raise Exception('could not parse inputs')
        print(output)
        await rpc.async_close_http_session()

    else:
        raise Exception('could not parse inputs')

