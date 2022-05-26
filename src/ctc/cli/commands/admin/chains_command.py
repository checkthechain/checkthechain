from __future__ import annotations

import toolcli
import toolstr

from ctc import config
from ctc import directory


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chains_command,
        'help': 'print information about configured chains',
    }


async def async_chains_command() -> None:
    directory_networks = directory.get_networks()
    config_networks = config.get_networks()
    default_network = config.get_default_network()

    all_networks = list(directory_networks.values()) + list(
        config_networks.values()
    )
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
        'has rpc',
        'default',
    ]
    rows = []
    for network in all_networks:

        if network['chain_id'] in already_used:
            continue
        already_used.add(network['chain_id'])

        is_default = '✓' if default_network == network['name'] else ''
        has_provider = '✓' if network['name'] in providers_by_chain else ''

        row = [
            network['name'],
            network['chain_id'],
            network['block_explorer'],
            has_provider,
            is_default,
        ]
        rows.append(row)

    rows = sorted(rows, key=lambda row: (row[3], row[4], -row[1]), reverse=True)  # type: ignore

    toolstr.print_text_box('EVM Chains')
    print()
    toolstr.print_table(
        rows,
        labels=labels,
        column_justify={
            'default': 'center',
            'has rpc': 'center',
        },
    )
