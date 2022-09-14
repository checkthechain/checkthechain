from __future__ import annotations

import toolcli
import toolstr

from ctc import cli
from ctc import config
from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chains_command,
        'help': 'display information about configured chains',
        'args': [
            {
                'name': ['--verbose', '-v'],
                'help': 'display additional information including RPC urls',
                'action': 'store_true',
            },
        ],
        'examples': ['', '--verbose'],
    }


async def async_chains_command(verbose: bool) -> None:

    default_network = config.get_default_network()
    all_networks = list(evm.get_networks().values())
    all_networks = sorted(all_networks, key=lambda network: network['chain_id'])

    # providers
    providers = config.get_providers()
    providers_by_chain = {
        provider['network']: provider for provider in providers.values()
    }

    already_used = set()
    labels = [
        'name',
        'chain_id',
        'block explorer',
        'default',
        'has rpc',
    ]
    if verbose:
        labels[4] = 'rpc'

    rows = []
    for network in all_networks:

        if network['chain_id'] in already_used:
            continue
        already_used.add(network['chain_id'])

        is_default = '✓' if default_network == network['chain_id'] else ''

        if not verbose:
            has_provider = '✓' if network['chain_id'] in providers_by_chain else ''
        else:
            if network['chain_id'] in providers_by_chain:
                has_provider = providers_by_chain[network['chain_id']]['url']
            else:
                has_provider = ''

        row = [
            network['name'],
            network['chain_id'],
            network['block_explorer'],
            is_default,
            has_provider,
        ]
        rows.append(row)

    rows = sorted(rows, key=lambda row: (row[3], row[4], -row[1]), reverse=True)  # type: ignore

    styles = cli.get_cli_styles()

    toolstr.print_text_box('EVM Chains', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        labels=labels,
        column_justify={
            'default': 'center',
            'has rpc': 'center',
        },
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'chain_id': styles['description'],
            'block explorer': styles['metavar'],
            'default': styles['title'],
            'has rpc': styles['title'],
        },
    )
