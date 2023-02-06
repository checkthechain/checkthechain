from __future__ import annotations

import os
import typing

import toolsql

from ctc import config
from ctc import spec
from .management import dba_utils
from .management import version_utils


def create_missing_schemas(
    schema_name: spec.SchemaName | None = None,
    *,
    schema_names: typing.Sequence[spec.SchemaName] | None = None,
    context: spec.Context = None,
):

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
        pathdir = os.path.dirname(os.path.abspath(db_config['path']))
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

