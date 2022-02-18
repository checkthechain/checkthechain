from ctc.protocols import ens_utils
from ctc import rpc


def get_command_spec():
    return {
        'f': async_exists_command,
        'args': [{'name': 'name'}],
    }


async def async_exists_command(name):
    exists = await ens_utils.async_record_exists(name)
    print(exists)
    await rpc.async_close_http_session()

