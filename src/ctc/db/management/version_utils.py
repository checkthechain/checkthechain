from __future__ import annotations

import threading
import typing

import sqlalchemy
import toolsql

import ctc
from ctc import config
from ctc import directory
from ctc import spec


_schema_version_cache = {
    'engine': None,
    'lock': threading.Lock(),
}


def is_schema_versions_initialized(engine: toolsql.SAEngine) -> bool:
    return sqlalchemy.inspect(engine).has_table('schema_versions')


def get_schema_version(
    schema_name: str,
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection | None = None,
) -> str | None:

    chain_id = directory.get_network_chain_id(network)

    if conn is None:
        engine = _get_schema_version_engine()
        with engine.begin() as conn:
            return toolsql.select(
                conn=conn,
                table='schema_versions',
                where_equals={'chain_id': chain_id, 'schema_name': schema_name},
                return_count='one',
                only_columns=['version'],
                row_format='only_column',
            )
    else:
        return toolsql.select(
            conn=conn,
            table='schema_versions',
            where_equals={'chain_id': chain_id, 'schema_name': schema_name},
            return_count='one',
            only_columns=['version'],
            row_format='only_column',
        )


def _get_schema_version_engine() -> toolsql.SAEngine:
    lock = typing.cast(threading.Lock, _schema_version_cache['lock'])
    with lock:
        if _schema_version_cache.get('engine') is None:
            db_config = config.get_db_config()
            _schema_version_cache['engine'] = toolsql.create_engine(
                db_config=db_config
            )
        return _schema_version_cache['engine']


def set_schema_version(
    schema_name: str,
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    version: str | None = None,
) -> None:

    if version is None:
        version = ctc.__version__

    chain_id = directory.get_network_chain_id(network)

    toolsql.insert(
        conn=conn,
        table='schema_versions',
        row={
            'chain_id': chain_id,
            'schema_name': schema_name,
            'version': version,
        },
    )
