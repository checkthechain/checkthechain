from __future__ import annotations

import typing

import toolcli
import toolsql

from ctc import config
from ctc import spec
from .. import connect_utils
from .. import schema_utils
from . import version_utils


async def async_create_evm_tables(
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
            missing_tables = toolsql.get_missing_tables(
                db_schema=schema,
                db_config=db_config,
            )
            tables_to_create += missing_tables['missing_from_db']

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
    # (for now, use same database for all tables)
    engine = connect_utils.create_engine(
        'schema_versions',
        network=None,
        create_missing_schema=False,
    )
    if engine is None:
        raise Exception('could not create engine for database')

    # initialize schema versions schema if need be
    with engine.begin() as conn:
        if not version_utils.is_schema_versions_initialized(engine=engine):
            initialize_schema_versions(conn=conn)

    with engine.begin() as conn:

        # create each schema for each used network
        for network in networks:
            for schema_name in schema_names:
                initialize_schema(
                    schema_name=schema_name,
                    network=network,
                    conn=conn,
                )

    print()
    print('all tables created')


def initialize_schema_versions(conn: toolsql.SAConnection) -> None:
    initialize_schema(
        'schema_versions',
        network=-1,
        conn=conn,
        prepared_schema=False,
    )


def initialize_schema(
    schema_name: schema_utils.SchemaName,
    network: spec.NetworkReference,
    conn: toolsql.SAConnection,
    prepared_schema: bool = True,
) -> None:
    """initialize schema by creating its table and other objects"""

    # check that schema versions are being tracked
    if not version_utils.is_schema_versions_initialized(engine=conn.engine):
        if schema_name != 'schema_versions':
            initialize_schema_versions(conn=conn)
    else:
        # check that schema not already initialized
        schema_version = version_utils.get_schema_version(
            schema_name=schema_name,
            network=network,
            conn=conn,
        )
        if schema_version is not None:
            raise Exception('schema already initialized')

    # load schema data
    if prepared_schema:
        schema = schema_utils.get_prepared_schema(
            schema_name=typing.cast(schema_utils.EVMSchemaName, schema_name),
            network=network,
        )
    else:
        schema = schema_utils.get_raw_schema(schema_name=schema_name)

    # create tables
    for table_name, table_schema in schema['tables'].items():
        toolsql.create_table(
            table_name,
            table_schema=table_schema,
            conn=conn,
        )

    # set version in schema version table
    version_utils.set_schema_version(
        schema_name=schema_name,
        network=network,
        conn=conn,
    )
