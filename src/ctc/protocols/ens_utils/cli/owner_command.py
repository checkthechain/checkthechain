from ctc.protocols import ens_utils
from ctc import rpc


def get_command_spec():
    return {
        'f': async_owner_command,
        'args': [{'name': 'name'}],
    }


async def async_owner_command(name):
    owner = await ens_utils.async_get_owner(name)
    print(owner)
    await rpc.async_close_http_session()

