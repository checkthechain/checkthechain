from ctc.protocols import ens_utils
from ctc import rpc


def get_command_spec():
    return {
        'f': async_records_command,
        'args': [
            {'name': 'name'},
        ],
    }


async def async_records_command(name):
    text_records = await ens_utils.async_get_text_records(name=name)

    for key, value in sorted(text_records.items()):
        print('-', key + ':', value)

    await rpc.async_close_http_session()

