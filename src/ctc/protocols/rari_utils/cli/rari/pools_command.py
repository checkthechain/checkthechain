import tooltable  # type: ignore
import tooltime

from ctc import rpc
from ctc.protocols import rari_utils


def get_command_spec():
    return {
        'f': pools_command,
        'help': 'list all Rari fuse pools',
        'args': [
            {
                'name': ['--verbose'],
                'help': 'emit extra output',
                'action': 'store_true',
            },
        ],
    }


async def pools_command(verbose):
    all_pools = await rari_utils.async_get_all_pools()
    rows = []
    for p, pool in enumerate(all_pools):
        if verbose:
            row = [
                p,  # index
                pool[0],  # name
                str(pool[3]),  # creation block
                tooltime.timestamp_to_iso(pool[4]),  # creation time
                pool[2],  # comptroller
                pool[1],  # creator
            ]
            headers = [
                'index',
                'name',
                'create block',
                'create time',
                'comptroller',
                'creator',
            ]
        else:
            row = [
                p,  # index
                pool[0][:20],  # name
                tooltime.timestamp_to_iso(pool[4])[:10],  # creation time
                pool[2],  # comptroller
            ]
            headers = ['index', 'name', 'date', 'comptroller']
        rows.append(row)
    print(len(rows))
    tooltable.print_table(rows, headers=headers)

    await rpc.async_close_http_session()

