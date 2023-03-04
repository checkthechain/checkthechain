from __future__ import annotations

import typing

import toolcli
import toolsql

import ctc.config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_create_tables_command,
        'help': 'create tables for database',
        'args': [
            {
                'name': '--schema-names',
                'nargs': '+',
                'help': 'schemas to create tables for',
            },
            {
                'name': '--networks',
                'nargs': '+',
                'help': 'networks to create tables for',
            },
        ],
        'examples': [''],
        'hidden': True,
    }


async def async_create_tables_command(
    schema_names: typing.Sequence[str],
    networks: typing.Sequence[str],
) -> None:
    from ctc import db

    if schema_names is not None:
        for schema_name in schema_names:
            if schema_name not in db.DBSchemaName.__args__:  # type: ignore
                raise Exception('unknown schema_name: ' + str(schema_name))

    db_config = ctc.config.get_context_db_config(
        context=None, schema_name=schema_name
    )
    with toolsql.connect(db_config) as conn:
        db.create_missing_tables(
            schema_names=schema_names,
            networks=networks,
            conn=conn,
        )

