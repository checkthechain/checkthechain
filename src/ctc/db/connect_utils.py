from __future__ import annotations

import os
import typing

import toolsql

from ctc import config
from ctc import spec

from . import schema_utils
from .management import dba_utils
from .management import version_utils


def create_engine(
    schema_name: schema_utils.SchemaName,
    *,
    network: spec.NetworkReference | None,
    create_missing_schema: bool = True,
) -> toolsql.SAEngine | None:
    """create sqlalchemy engine object"""

    # get db config
    data_source: config.DataSource | config.LeafDataSource = (
        config.get_data_source(datatype=schema_name, network=network)
    )
    if data_source['backend'] == 'hybrid':
        data_source = typing.cast(config.DataSource, data_source)[
            'hybrid_order'
        ][0]
    if data_source.get('backend') != 'db' or 'db_config' not in data_source:
        raise Exception('not using database for this type of data')
    db_config = data_source['db_config']
    if db_config is None:
        raise Exception('invalid db_config')

    # create directory if need be
    if db_config['dbms'] == 'sqlite':
        pathdir = os.path.dirname(os.path.abspath(db_config['path']))
        os.makedirs(pathdir, exist_ok=True)

    # create engine
    engine = toolsql.create_engine(db_config=db_config)

    # create missing tables
    if create_missing_schema:
        with engine.begin() as conn:

            # check that schema versions being tracked
            if not version_utils.is_schema_versions_initialized(engine=engine):
                dba_utils.initialize_schema_versions(conn=conn)

            # check if schema in database
            schema_version = version_utils.get_schema_version(
                schema_name=schema_name,
                network=network,
            )

            # create schema if missing
            if schema_version is None:
                dba_utils.initialize_schema(
                    schema_name=schema_name,
                    network=network,
                    conn=conn,
                )

    return engine
