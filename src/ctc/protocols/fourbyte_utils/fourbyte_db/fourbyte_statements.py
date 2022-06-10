from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ctc import db
from .. import fourbyte_spec
from . import fourbyte_schema_defs


async def async_upsert_function_entry(
    function_entry: fourbyte_spec.Entry,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    table = db.get_table_name('function_signatures', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row=function_entry,
        upsert='do_update',
    )


async def async_upsert_function_entries(
    function_entries: typing.Sequence[fourbyte_spec.Entry],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    table = db.get_table_name('function_signatures', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=function_entries,
        upsert='do_update',
    )


async def async_select_function_entries(
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    hex_signature: str | None = None,
    text_signature: str | None = None,
) -> typing.Sequence[fourbyte_spec.Entry] | None:

    table = db.get_table_name('function_signatures', network=network)

    where_equals = {
        'hex_signature': hex_signature,
        'text_signature': text_signature,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    return toolsql.select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        raise_if_table_dne=False,
    )


async def async_delete_function_entries(
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    hex_signature: str | None = None,
    text_signature: str | None = None,
) -> None:

    table = db.get_table_name('function_signatures', network=network)

    where_equals = {
        'hex_signature': hex_signature,
        'text_signature': text_signature,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }
    if len(where_equals) == 0:
        raise Exception('must specify which feeds to delete')

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals=where_equals,
    )
