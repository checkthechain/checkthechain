from __future__ import annotations

import os
import typing

import toolsql

from ctc import config
from ctc import spec
from .management import dba_utils
from .management import version_utils


def create_engine(
    schema_name: spec.SchemaName | None = None,
    *,
    schema_names: typing.Sequence[spec.SchemaName] | None = None,
    context: spec.Context = None,
    create_missing_schema: bool = True,
) -> toolsql.SAEngine | None:
    """create sqlalchemy engine object

    TODO: modify behavior of `schema_names` parameter once multicaches supported
    """

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

    network = config.get_context_chain_id(context)

    # get db config
    db_config = config.get_context_db_config(
        context=context, schema_name=schema_name
    )

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

            for schema_name in schema_names:

                # check if schema in database
                schema_version = version_utils.get_schema_version(
                    schema_name=schema_name,
                    context=dict(network=network),
                )

                # create schema if missing
                if schema_version is None:
                    dba_utils.initialize_schema(
                        schema_name=schema_name,
                        context=context,
                        conn=conn,
                    )

    return engine

