from ctc.protocols import ens_utils
from ctc import rpc


def get_command_spec():
    return {
        'f': async_resolve_command,
        'args': [
            {'name': 'name'},
        ]
    }


async def async_resolve_command(name):
    address = await ens_utils.async_resolve_name(name)
    print(address)
    await rpc.async_close_http_session()

