from __future__ import annotations

import typing

import toolsql

import ctc


async def async_upsert_schema_update(
    table_name: str,
    version: str | None = None,
    *,
    conn: toolsql.SAConnection,
    upsert: bool = True,
) -> None:

    if version is None:
        version = ctc.__version__

    # construct row
    row = {
        'table_name': table_name,
        'version': version,
    }

    # get upsert option
    if upsert:
        upsert_option: toolsql.ConflictOption | None = 'do_update'
    else:
        upsert_option = None

    # insert data
    toolsql.insert(
        conn=conn,
        table='schema_updates',
        row=row,
        upsert=upsert_option,
    )


async def async_select_schema_updates(
    conn: toolsql.SAConnection,
    table_name: str | None = None,
) -> typing.Sequence[typing.Mapping[typing.Any, typing.Any]]:

    if table_name is not None:
        where_equals = {'table_name': table_name}
    else:
        where_equals = {}

    return toolsql.select(
        conn=conn,
        table='schema_updates',
        where_equals=where_equals,
    )


async def async_delete_schema_updates(
    conn: toolsql.SAConnection,
    table_name: str,
) -> None:
    return toolsql.delete(
        conn=conn,
        table='schema_updates',
        where_equals={'table_name': table_name},
    )
