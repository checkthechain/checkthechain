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

    # get confirmation
    if not confirm:
        if not toolcli.input_yes_or_no('continue? '):
            raise Exception('aborted creation of tables')

    # create tables
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
            toolsql.create_tables(
                db_schema=schema,
                db_config=db_config,
            )

