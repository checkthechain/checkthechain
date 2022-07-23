from __future__ import annotations

import threading
import typing

import sqlalchemy  # type: ignore
import toolsql

import ctc
from ctc import config
from ctc import evm
from ctc import spec

from .. import schema_utils

_schema_version_cache = {
    'engine': None,
    'lock': threading.Lock(),
}


def is_schema_versions_initialized(engine: toolsql.SAEngine) -> bool:
    result = sqlalchemy.inspect(engine).has_table('schema_versions')
    if not isinstance(result, bool):
        raise Exception('invalid result')
    return result


def get_schema_version(
    schema_name: str,
    network: spec.NetworkReference | None,
    *,
    conn: toolsql.SAConnection | None = None,
) -> str | None:

    if network is None:
        # use chain_id = -1 for dbs that have no network association
        if schema_name not in schema_utils.get_network_schema_names():
            chain_id = -1
        else:
            raise Exception(
                'must specify network for schema ' + str(schema_name)
            )
    else:
        chain_id = evm.get_network_chain_id(network)

    if conn is None:
        engine = _get_schema_version_engine()
        with engine.begin() as conn:
            result = toolsql.select(
                conn=conn,
                table='schema_versions',
                where_equals={'chain_id': chain_id, 'schema_name': schema_name},
                return_count='one',
                only_columns=['version'],
                row_format='only_column',
            )
    else:
        result = toolsql.select(
            conn=conn,
            table='schema_versions',
            where_equals={'chain_id': chain_id, 'schema_name': schema_name},
            return_count='one',
            only_columns=['version'],
            row_format='only_column',
        )

    if result is not None and not isinstance(result, str):
        raise Exception('invalid result format')
    return result


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
    *,
    conn: toolsql.SAConnection,
    version: str | None = None,
) -> None:

    if version is None:
        version = ctc.__version__

    if network is None:
        # use chain_id = -1 for dbs that have no network association
        if schema_name not in schema_utils.get_network_schema_names():
            chain_id = -1
        else:
            raise Exception(
                'must specify network for schema ' + str(schema_name)
            )
    else:
        chain_id = evm.get_network_chain_id(network)

    toolsql.insert(
        conn=conn,
        table='schema_versions',
        row={
            'chain_id': chain_id,
            'schema_name': schema_name,
            'version': version,
        },
    )


def delete_schema_version(
    schema_name: str | None,
    network: spec.NetworkReference | None,
    *,
    conn: toolsql.SAConnection,
    confirm_delete_row: bool = False,
    confirm_delete_network: bool = False,
    confirm_delete_schema: bool = False,
    confirm_delete_all: bool = False,
) -> None:

    if schema_name is None and network is None:
        if not confirm_delete_all:
            import toolcli

            answer = toolcli.input_yes_or_no(
                'delete ALL version rows for ALL schemas? '
            )
            if not answer:
                raise Exception('aborting')

    elif schema_name is not None and network is not None:
        if not confirm_delete_row:
            import toolcli

            answer = toolcli.input_yes_or_no(
                'delete version row for schema '
                + schema_name
                + ' for network '
                + str(network)
                + ' ? '
            )
            if not answer:
                raise Exception('aborting')

    elif schema_name is not None:
        if not confirm_delete_schema:
            import toolcli

            answer = toolcli.input_yes_or_no(
                'delete ALL version rows for schema ' + schema_name + '? '
            )
            if not answer:
                raise Exception('aborting')

    elif network is not None:
        if not confirm_delete_network:
            import toolcli

            answer = toolcli.input_yes_or_no(
                'delete ALL version rows for network ' + str(network) + '? '
            )
            if not answer:
                raise Exception('aborting')

    where_equals: typing.MutableMapping[str, typing.Any] = {}
    if schema_name is not None:
        where_equals['schema_name'] = schema_name
    if network is not None:
        where_equals['chain_id'] = evm.get_network_chain_id(network)

    toolsql.delete(
        conn=conn,
        table='schema_versions',
        where_equals=where_equals,
    )
