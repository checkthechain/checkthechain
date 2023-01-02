from __future__ import annotations

import os

import toolsql

from ctc import config
from ctc import spec
from .management import dba_utils
from .management import version_utils


def create_engine(
    schema_name: spec.SchemaName,
    *,
    context: spec.Context = None,
    create_missing_schema: bool = True,
) -> toolsql.SAEngine | None:
    """create sqlalchemy engine object"""

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

