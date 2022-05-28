from __future__ import annotations

import typing

import toolcli
import toolsql

from ctc import config
from ctc import spec
from .. import schema_utils


def create_evm_tables(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
    schema_names: typing.Sequence[schema_utils.EVMSchemaName] | None = None,
    verbose: bool = True,
    confirm: bool = False,
) -> None:

    # get netowrks and schemas
    if networks is None:
        networks = config.get_used_networks()
    if schema_names is None:
        schema_names = schema_utils.get_evm_schema_names()

    # get preamble
    if verbose or not confirm:
        print(
            'creating tables for',
            len(schema_names),
            'schema(s) across',
            len(networks),
            'network(s)',
        )
        if len(schema_names) > 1:
            print('    - schemas:')
            for schema_name in schema_names:
                print('        -', schema_name)
        else:
            print('    - schema:', schema_name)
        if len(networks) > 1:
            print('    - networks:')
            for network in networks:
                print('        -', network)
        else:
            print('    - network:', network)

    # get missing tables
    tables_to_create: list[str] = []
    for network in networks:
        for schema_name in schema_names:
            db_config = config.get_db_config(
                network=network,
                schema_name=schema_name,
                require=True,
            )
            schema = schema_utils.get_prepared_schema(
                schema_name=schema_name,
                network=network,
            )
            tables_to_create += toolsql.get_missing_tables(
                db_schema=schema,
                db_config=db_config,
            )

    # print missing tables
    if len(tables_to_create) == 0:
        print()
        print('all tables already exist')
        return
    else:
        print()
        print('tables to create:')
        for table in tables_to_create:
            print('-', table)

    # get confirmation
    if not confirm:
        print()
        if not toolcli.input_yes_or_no('continue? '):
            raise Exception('aborted creation of tables')

    # create tables
    print()
    for network in networks:
        for schema_name in schema_names:
            schema = schema_utils.get_prepared_schema(
                schema_name=schema_name,
                network=network,
            )
            toolsql.create_tables(
                db_schema=schema,
                db_config=db_config,
            )
