from __future__ import annotations

import toolcli
import toolstr

from ctc.protocols.chainlink_utils import chainlink_db


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chainlink_ls_command,
        'help': 'list all Chainlink feeds',
        'args': [
            {
                'name': 'query',
                'nargs': '?',
                'help': 'partial match of feed name, case insensitive',
            },
        ],
        'examples': [
            '',
            'DAI',
        ],
    }


async def async_chainlink_ls_command(query: str) -> None:
    oracle_feeds = await chainlink_db.async_query_feeds(network='mainnet')
    if oracle_feeds is None:
        return
    rows = []
    for feed in oracle_feeds:
        if feed is None:
            continue
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
    toolstr.print_table(
        rows,
        labels=labels,
        column_gap=1,
        column_widths=[20, 5, 4, 42],
    )
