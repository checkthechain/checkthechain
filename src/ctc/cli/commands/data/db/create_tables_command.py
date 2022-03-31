from __future__ import annotations

from ctc import db


def get_command_spec():
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


async def async_create_tables_command(datatypes, networks):
    db.create_tables(
        datatypes=datatypes,
        networks=networks,
    )

