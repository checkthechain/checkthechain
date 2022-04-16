from __future__ import annotations

import typing

import toolcli

from ctc import db


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_create_tables_command,
        'help': 'create tables for database',
        'args': [
            {
                'name': '--datatypes',
                'nargs': '+',
                'help': 'datatypes to create tables for',
            },
            {
                'name': '--networks',
                'nargs': '+',
                'help': 'networks to create tables for',
            },
        ],
    }


async def async_create_tables_command(
    datatypes: typing.Sequence[str],
    networks: typing.Sequence[str],
) -> None:
    db.create_tables(
        datatypes=datatypes,
        networks=networks,
    )

