from __future__ import annotations

import typing

import toolcli

from ctc import db


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': drop_command,
        'args': [
            {'name': 'schema_name', 'help': 'schema to drop'},
            {
                'name': 'network',
                'nargs': '?',
                'help': 'drop schema for single network, leave blank for all networks',
            },
            {
                'name': '--confirm',
                'help': 'confirm that schema should be dropped',
                'action': 'store_true',
            },
        ],
        'help': 'drop schema from db',
        'examples': [
            'blocks mainnnet',
            'blocks arbitrum',
        ],
        'hidden': True,
    }


def drop_command(
    *, schema_name: str, network: str | int, confirm: bool
) -> None:

    if isinstance(network, str):
        if network.isdigit() or (network[0] == '-' and network[1:].isdigit()):
            network = int(network)

    db.drop_schema(
        schema_name=typing.cast(db.SchemaName, schema_name),
        network=network,
        confirm=confirm,
    )
