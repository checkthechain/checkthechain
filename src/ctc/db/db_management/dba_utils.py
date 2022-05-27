from __future__ import annotations

import typing

import toolcli
import toolsql

from ctc import config
from ctc import spec
from .. import db_schemas
from .. import db_spec


def create_tables(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
    datatypes: typing.Sequence[db_spec.DBDatatype] | None = None,
    verbose: bool = True,
    confirm: bool = False,
) -> None:

    # get netowrks and datatypes
    if networks is None:
        networks = config.get_used_networks()
    if datatypes is None:
        datatypes = db_spec.get_all_datatypes()

    # get preamble
    if verbose or not confirm:
        print(
            'creating tables for',
            len(datatypes),
            'datatype(s) across',
            len(networks),
            'network(s)',
        )
        if len(datatypes) > 1:
            print('    - datatypes:')
            for datatype in datatypes:
                print('        -', datatype)
        else:
            print('    - datatype:', datatype)
        if len(networks) > 1:
            print('    - networks:')
            for network in networks:
                print('        -', network)
        else:
            print('    - network:', network)

    # get missing tables
    tables_to_create = []
    for network in networks:
        for datatype in datatypes:
            db_config = config.get_db_config(
                network=network,
                datatype=datatype,
                require=True,
            )
            schema = db_schemas.get_prepared_schema(
                datatype=datatype,
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
        for datatype in datatypes:
            toolsql.create_tables(
                db_schema=schema,
                db_config=db_config,
            )
