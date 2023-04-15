# MOVE create_missing_schemas TO dba_utils

from __future__ import annotations

import os
import typing

import toolsql

from ctc import config
from ctc import spec
from .management import dba_utils
from .management import version_utils


def connect(
    context: spec.Context,
    schema: spec.SchemaName,
    *,
    read_only: bool = False,
    db_config: toolsql.DBConfig | None = None,
) -> toolsql.Connection:
    if db_config is None:
        db_config = config.get_context_db_config(
            context=context, schema_name=schema
        )
    if read_only:
        db_config = db_config.copy()
        db_config['driver'] = 'connectorx'
    return toolsql.connect(db_config)


def async_connect(
    context: spec.Context,
    schema: spec.SchemaName,
    *,
    read_only: bool = False,
    db_config: toolsql.DBConfig | None = None,
) -> toolsql.AsyncConnection:
    if db_config is None:
        db_config = config.get_context_db_config(
            context=context, schema_name=schema
        )
    if read_only:
        db_config = db_config.copy()
        db_config['driver'] = 'connectorx'
    return toolsql.async_connect(db_config)


def create_missing_schemas(
    schema_name: spec.SchemaName | None = None,
    *,
    schema_names: typing.Sequence[spec.SchemaName] | None = None,
    context: spec.Context = None,
) -> None:

    if schema_name is not None and schema_names is not None:
        raise Exception('specify only one of schema_name or schema_names')
    if schema_name is None:
        if schema_names is None or len(schema_names) == 0:
            raise Exception('must specify schema_name or schema_names')
        else:
            schema_name = schema_names[0]
    if schema_names is None:
        if schema_name is None:
            raise Exception('must specify schema_name or schema_names')
        else:
            schema_names = [schema_name]

    # get db config
    db_config = config.get_context_db_config(
        context=context, schema_name=schema_name
    )

    # create directory if need be
    if db_config['dbms'] == 'sqlite':
        path = db_config['path']
        if path is None:
            raise Exception('sqlite path not specified')
        pathdir = os.path.dirname(os.path.abspath(path))
        if pathdir is None:
            raise Exception('invalid path dir')
        os.makedirs(pathdir, exist_ok=True)

    # create missing tables
    network = config.get_context_chain_id(context)
    with toolsql.connect(db_config) as conn:

        # check that schema versions being tracked
        if not version_utils.is_schema_versions_initialized(conn=conn):
            dba_utils.initialize_schema_versions(conn=conn)

        for schema_name in schema_names:

            # check if schema in database
            schema_version = version_utils.get_schema_version(
                schema_name=schema_name,
                context=dict(network=network),
                conn=conn,
            )

            # create schema if missing
            if schema_version is None:
                dba_utils.initialize_schema(
                    schema_name=schema_name,
                    context=context,
                    conn=conn,
                )

