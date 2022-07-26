from __future__ import annotations

import typing

import sqlalchemy  # type: ignore
import toolcli
import toolsql

from ctc import config
from ctc import spec
from .. import connect_utils
from .. import schema_utils
from . import version_utils


def create_missing_tables(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
    schema_names: typing.Sequence[schema_utils.SchemaName] | None = None,
    *,
    db_config: toolsql.DBConfig | None = None,
    verbose: bool = True,
    confirm: bool = False,
) -> None:
    network_schema_names = schema_utils.get_network_schema_names()
    generic_schema_names = schema_utils.get_generic_schema_names()

    # get netowrks and schemas
    if networks is None:
        networks = config.get_networks_that_have_providers()
    if schema_names is None:
        schema_names = network_schema_names + generic_schema_names

    # get preamble
    if verbose or not confirm:
        print(
            'Actively using',
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
        elif len(networks) == 1:
            print('    - network:', networks[0])
        else:
            print()
            print('No networks specified, creating no tables')

    # using single db config for all schemas
    if db_config is None:
        db_config = config.get_db_config(
            schema_name='schema_versions',
            network=None,
            require=True,
        )

    # get missing tables
    schemas_to_create: list[
        tuple[spec.NetworkReference | None, schema_utils.SchemaName]
    ] = []
    for schema_name in schema_names:

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
                    schema_name=typing.cast(
                        schema_utils.NetworkSchemaName, schema_name
                    ),
                    network=schema_network,
                )
            else:
                schema = schema_utils.get_raw_schema(schema_name=schema_name)

            missing_tables = toolsql.get_missing_tables(
                db_schema=schema,
                db_config=db_config,
            )
            if len(missing_tables['missing_from_db']) > 0:
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
    engine = toolsql.create_engine(db_config=db_config)
    if engine is None:
        raise Exception('Could not create engine for database')

    # initialize schema versions schema if need be
    with engine.begin() as conn:
        if not version_utils.is_schema_versions_initialized(engine=engine):
            initialize_schema_versions(conn=conn)

    with engine.begin() as conn:

        # create each schema for each used network
        for schema_network, schema_name in schemas_to_create:
            initialize_schema(
                schema_name=schema_name,
                network=schema_network,
                conn=conn,
            )

    print()
    print('All tables created')


def initialize_schema_versions(conn: toolsql.SAConnection) -> None:
    """initialize the schema_versions schema which manages versions of schemas"""
    initialize_schema(
        'schema_versions',
        network=None,
        conn=conn,
    )


def initialize_schema(
    schema_name: schema_utils.SchemaName,
    *,
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
) -> None:
    """initialize schema by creating its table and other objects"""

    network_schema_names = schema_utils.get_network_schema_names()
    prepared_schema = schema_name in network_schema_names

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
            schema_name=typing.cast(
                schema_utils.NetworkSchemaName, schema_name
            ),
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

    toolsql.clear_table_caches(conn=conn)


def drop_schema(
    schema_name: schema_utils.SchemaName,
    network: spec.NetworkReference | None = None,
    *,
    confirm: bool = False,
) -> None:

    if not confirm:
        if network is not None:
            answer = toolcli.input_yes_or_no(
                'Delete version row for schema '
                + schema_name
                + ' for network '
                + str(network)
                + '? '
            )
            if not answer:
                raise Exception('aborting')
        else:
            answer = toolcli.input_yes_or_no(
                'Delete ALL version rows for schema ' + schema_name + '? '
            )
            if not answer:
                raise Exception('aborting')

    if network is None:
        if schema_name in schema_utils.get_network_schema_names():
            networks: typing.Sequence[
                spec.NetworkReference | None
            ] = config.get_networks_that_have_providers()
        else:
            networks = [None]
    else:
        networks = [network]

    for network in networks:

        # determine tables in db
        engine = connect_utils.create_engine(
            schema_name=schema_name,
            network=network,
            create_missing_schema=False,
        )
        if engine is None:
            continue
        db_table_names = sqlalchemy.inspect(engine).get_table_names()

        # determine tables in schema
        if network is not None:
            schema_data = schema_utils.get_prepared_schema(
                schema_name=typing.cast(
                    schema_utils.NetworkSchemaName, schema_name
                ),
                network=network,
            )
        else:
            schema_data = schema_utils.get_raw_schema(schema_name=schema_name)
        schema_table_names = schema_data['tables']

        # determine which tables to drop
        drop_table_names = set(db_table_names) & set(schema_table_names)

        # drop schema tables
        with engine.begin() as conn:
            for table_name in drop_table_names:
                print('Dropping table', table_name)
                table_object = toolsql.create_table_object_from_db(
                    engine=engine,
                    table_name=table_name,
                )
                table_object.drop(bind=engine)

    # delete rows from schema_versions table
    schema_version_engine = connect_utils.create_engine(
        schema_name='schema_versions',
        network=None,
        create_missing_schema=False,
    )
    if schema_version_engine is not None:
        with schema_version_engine.begin() as conn:
            for network in networks:
                version_utils.delete_schema_version(
                    schema_name=schema_name,
                    network=network,
                    conn=conn,
                    confirm_delete_row=True,
                    confirm_delete_schema=True,
                )
