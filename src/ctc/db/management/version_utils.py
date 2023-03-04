from __future__ import annotations

import typing

import toolsql

import ctc
from ctc import config
from ctc import evm
from ctc import spec

from .. import schema_utils


def is_schema_versions_initialized(conn: toolsql.Connection) -> bool:
    return 'schema_versions' in toolsql.get_table_names(conn)


def get_schema_version(
    schema_name: str,
    *,
    context: spec.Context,
    conn: toolsql.Connection,
) -> str | None:

    # use chain_id = -1 for dbs that have no network association
    if schema_name not in schema_utils.get_network_schema_names():
        chain_id = -1
    else:
        chain_id = config.get_context_chain_id(context)

    result = toolsql.select(
        conn=conn,
        table='schema_versions',
        where_equals={'chain_id': chain_id, 'schema_name': schema_name},
        columns=['version'],
        output_format='cell_or_none',
    )

    if result is not None and not isinstance(result, str):
        raise Exception('invalid result format')

    return result


def set_schema_version(
    schema_name: str,
    *,
    context: spec.Context,
    conn: toolsql.Connection,
    version: str | None = None,
) -> None:

    if version is None:
        version = ctc.__version__

    # use chain_id = -1 for dbs that have no network association
    if schema_name not in schema_utils.get_network_schema_names():
        chain_id = -1
    else:
        chain_id = config.get_context_chain_id(context)

    row = {'chain_id': chain_id, 'schema_name': schema_name, 'version': version}
    toolsql.insert(row=row, conn=conn, table='schema_versions')


def delete_schema_version(
    schema_name: str | None,
    *,
    network: spec.NetworkReference | None,
    conn: toolsql.Connection,
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

