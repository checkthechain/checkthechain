from __future__ import annotations

import toolcli
import toolstr

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
    labels = ['name', 'delta', 'rate', 'address']
    print(len(rows))
    toolstr.print_table(rows, labels=labels)
