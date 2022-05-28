from __future__ import annotations

import typing

import toolsql


async def async_upsert_schema_update(
    table_name: str,
    version: str,
    conn: toolsql.SAConnection,
    upsert: bool = True,
) -> None:

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
    table_name: str,
) -> typing.Sequence[typing.Mapping[typing.Any, typing.Any]]:

    return toolsql.select(
        conn=conn,
        table='schema_updates',
        where_equals={'table_name': table_name},
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
