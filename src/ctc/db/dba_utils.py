from __future__ import annotations

import typing

import toolcli
import toolsql

from ctc import config
from ctc import spec
from . import schema_utils


def create_tables(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
    datatypes: typing.Sequnce[str] | None = None,
    verbose: bool = True,
    confirm: bool = True,
) -> None:

    # get netowrks and datatypes
    if networks is None:
        networks = config.get_used_networks()
    if datatypes is None:
        datatypes = schema_utils.get_all_datatypes()

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
            )
            db_schema = schema_utils.get_prepared_schema(
                datatype=datatype,
                network=network,
            )
            toolsql.create_tables(
                db_schema=db_schema,
                db_config=db_config,
            )

