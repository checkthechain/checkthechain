from __future__ import annotations

import toolcli
import toolstr

from ctc import config
from ctc import evm
from ctc import cli
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
            {
                'name': '--network',
                'help': 'network to list feeds of',
            },
        ],
        'examples': [
            '',
            'DAI',
        ],
    }


async def async_chainlink_ls_command(
    query: str, network: str | int | None
) -> None:

    context = config.create_user_input_context(network=network)

    oracle_feeds = await chainlink_db.async_query_feeds(context=context)
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
    styles = cli.get_cli_styles()
    network_name = evm.get_network_name(config.get_context_chain_id(context))
    toolstr.print_text_box(
        'Chainlink feeds on ' + network_name.title(),
        style=styles['title'],
    )
    toolstr.print_table(
        rows,
        labels=labels,
        column_gap=1,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'name': styles['option'],
            'delta': styles['description'],
            'rate': styles['description'],
            'address': styles['metavar'],
        },
        max_column_widths={'name': 14},
    )

