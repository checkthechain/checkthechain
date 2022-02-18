from ctc.protocols import ens_utils
from ctc import rpc


def get_command_spec():
    return {
        'f': async_reverse_command,
        'args': [
            {'name': 'name'},
        ]
    }


async def async_reverse_command(name):
    address = await ens_utils.async_reverse_lookup(name)
    print(address)
    await rpc.async_close_http_session()

