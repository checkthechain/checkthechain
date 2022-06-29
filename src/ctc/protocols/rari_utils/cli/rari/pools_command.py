from __future__ import annotations

import toolcli
import toolstr
import tooltime

from ctc.protocols import rari_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_pools_command,
        'help': 'list all Rari fuse pools',
        'args': [
            {
                'name': ['--verbose'],
                'help': 'emit extra output',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            '--verbose',
        ],
    }


async def async_pools_command(verbose: bool) -> None:
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
            labels = [
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
            labels = ['index', 'name', 'date', 'comptroller']
        rows.append(row)
    print(len(rows))
    toolstr.print_table(rows, labels=labels)
