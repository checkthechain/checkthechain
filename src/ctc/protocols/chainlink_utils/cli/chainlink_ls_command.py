from __future__ import annotations

import toolcli
import tooltable  # type: ignore

from ctc import directory


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': chainlink_ls_command,
        'help': 'list all Chainlink feeds',
        'args': [
            {
                'name': 'query',
                'nargs': '?',
                'help': 'partial match of feed name, case insensitive',
            },
        ],
    }


def chainlink_ls_command(query: str) -> None:
    oracle_feeds = directory.load_oracle_feeds(protocol='chainlink')
    rows = []
    for feed in oracle_feeds.values():
        if query is not None and query.lower() not in feed['name'].lower():
            continue
        row = [
            feed['name'],
            feed['deviation'],
            feed['heartbeat'],
            feed['address'][:42],
        ]
        rows.append(row)
    headers = ['name', 'deviation', 'heartbeat', 'address']
    print(len(rows))
    tooltable.print_table(rows, headers=headers)

