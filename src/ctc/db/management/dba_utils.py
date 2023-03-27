from __future__ import annotations

import typing

import toolcli
import toolsql

from ctc import config
from ctc import spec
from ctc.spec.typedefs import db_types
from .. import schema_utils
from . import version_utils


def create_missing_tables(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
    schema_names: typing.Sequence[str] | None = None,
    *,
    conn: toolsql.Connection,
    verbose: bool = True,
    confirm: bool = False,
) -> None:

    # get netowrks and schemas
    network_schema_names = schema_utils.get_network_schema_names()
    generic_schema_names = schema_utils.get_generic_schema_names()
    if networks is None:
        networks = config.get_networks_that_have_providers()
    if schema_names is None:
        schema_names = network_schema_names + generic_schema_names

    # get preamble
    if verbose or not confirm:
        n_schemas = len(schema_names)
        n_networks = len(networks)
        print('Using', n_schemas, 'schema(s) over', n_networks, 'network(s)')
        if len(schema_names) > 1:
            print('    - schemas:')
            for schema_name in schema_names:
                print('        -', schema_name)
        elif len(schema_names) == 1:
            print('    - schema:', schema_names[0])
        else:
            print('    - schema: [none specified]')
        if len(networks) > 1:
            print('    - networks:')
            for network in networks:
                print('        -', network)
        elif len(networks) == 1:
            print('    - network:', networks[0])
        else:
            print()
            print('No networks specified, creating no tables')

    # get missing tables
    schemas_to_create: list[
        tuple[spec.NetworkReference | None, spec.SchemaName]
    ] = []
    for schema_name_raw in schema_names:

        if schema_name_raw in schema_utils.get_all_schema_names():
            schema_name = typing.cast(db_types.SchemaName, schema_name_raw)
        else:
            raise Exception('unknown schema name: ' + str(schema_name_raw))

        # determine schema networks
        if schema_name in network_schema_names:
            schema_networks: typing.Sequence[
                spec.NetworkReference | None
            ] = networks
        else:
            schema_networks = [None]

        for schema_network in schema_networks:

            if schema_network is not None:
                schema = schema_utils.get_prepared_schema(
                    schema_name=schema_name,
                    context=dict(network=schema_network),
                )
            else:
                schema = schema_utils.get_raw_schema(schema_name=schema_name)

            # if any tables missing, mark schema for creation
            tables_in_db = toolsql.get_table_names(conn=conn)
            missing_tables = [
                table
                for table in schema['tables'].keys()
                if table not in tables_in_db
            ]
            if len(missing_tables) > 0:
                schemas_to_create.append((schema_network, schema_name))

    # print missing tables
    if len(schemas_to_create) == 0:
        print()
        print('All tables already exist')
        return
    else:
        print()
        print('Schemas to create:')
        for schema_network, schema_name in schemas_to_create:
            print('-', schema_name, '[network = ' + str(schema_network) + ']')

    # get confirmation
    if not confirm:
        print()
        if not toolcli.input_yes_or_no('continue? '):
            raise Exception('Skipping creation of tables')

    # create tables
    # (for now, use same database for all tables)

    # initialize schema versions schema if need be
    if not version_utils.is_schema_versions_initialized(conn=conn):
        initialize_schema_versions(conn=conn)

    # create each schema for each used network
    for schema_network, schema_name in schemas_to_create:
        initialize_schema(
            schema_name=schema_name,
            context=dict(network=schema_network),
            conn=conn,
        )

    print()
    print('All tables created')


def initialize_schema_versions(conn: toolsql.Connection) -> None:
    """initialize the schema_versions schema which manages versions of schemas"""

    initialize_schema('schema_versions', context=dict(network=None), conn=conn)


def initialize_schema(
    schema_name: spec.SchemaName,
    *,
    context: spec.Context,
    conn: toolsql.Connection,
) -> None:
    """initialize schema by creating its table and other objects"""

    network_schema_names = schema_utils.get_network_schema_names()
    prepared_schema = schema_name in network_schema_names

    # check that schema versions are being tracked
    if not version_utils.is_schema_versions_initialized(conn=conn):
        if schema_name != 'schema_versions':
            initialize_schema_versions(conn=conn)
    else:
        # check that schema not already initialized
        schema_version = version_utils.get_schema_version(
            schema_name=schema_name,
            context=context,
            conn=conn,
        )
        if schema_version is not None:
            raise Exception('schema already initialized')

    # load schema data
    if prepared_schema:
        schema = schema_utils.get_prepared_schema(
            schema_name=schema_name,
            context=context,
        )
    else:
        schema = schema_utils.get_raw_schema(schema_name=schema_name)

    # create tables
    for table_name, table_schema in schema['tables'].items():
        toolsql.create_table(
            table_schema,
            conn=conn,
            if_not_exists=True,
            confirm=True,
        )

    version_utils.set_schema_version(
        schema_name=schema_name,
        context=context,
        conn=conn,
    )


def drop_schema(
    schema_name: str,
    *,
    context: spec.Context = None,
    conn: toolsql.Connection,
    confirm: bool = False,
) -> None:

    if schema_name not in schema_utils.get_all_schema_names():
        raise Exception('unknown schema name: ' + str(schema_name))
    schema = typing.cast(db_types.SchemaName, schema_name)

    network: int | str | None = config.get_context_chain_id(context)
    if not confirm:
        if network is not None:
            answer = toolcli.input_yes_or_no(
                'Delete version row for schema '
                + schema
                + ' for network '
                + str(network)
                + '? '
            )
            if not answer:
                raise Exception('aborting')
        else:
            answer = toolcli.input_yes_or_no(
                'Delete ALL version rows for schema ' + schema + '? '
            )
            if not answer:
                raise Exception('aborting')

    if network is None:
        if schema in schema_utils.get_network_schema_names():
            networks: typing.Sequence[
                spec.NetworkReference | None
            ] = config.get_networks_that_have_providers()
        else:
            networks = [None]
    else:
        networks = [network]

    for network in networks:

        # determine tables in db
        db_table_names = toolsql.get_table_names(conn=conn)

        # determine tables in schema
        if network is not None:
            schema_data = schema_utils.get_prepared_schema(
                schema_name=schema,
                context=context,
            )
        else:
            schema_data = schema_utils.get_raw_schema(schema_name=schema)
        schema_table_names = schema_data['tables']

        # determine which tables to drop
        drop_table_names = set(db_table_names) & set(schema_table_names)

        # drop schema tables
        for table_name in drop_table_names:
            print('Dropping table', table_name)
            toolsql.drop_table(table=table_name, conn=conn, confirm=True)

    # delete rows from schema_versions table
    for network in networks:
        version_utils.delete_schema_version(
            schema_name=schema,
            network=network,
            conn=conn,
            confirm_delete_row=True,
            confirm_delete_schema=True,
        )

