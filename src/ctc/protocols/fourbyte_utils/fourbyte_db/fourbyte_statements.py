from __future__ import annotations

import typing

import toolsql

from .. import fourbyte_spec


#
# # functions
#


async def async_upsert_function_signature(
    function_signature: fourbyte_spec.PartialEntry,
    conn: toolsql.SAConnection,
) -> None:

    toolsql.insert(
        conn=conn,
        table='function_signatures',
        row=function_signature,
        upsert='do_update',
    )


async def async_upsert_function_signatures(
    function_signatures: typing.Sequence[fourbyte_spec.PartialEntry],
    conn: toolsql.SAConnection,
) -> None:

    toolsql.insert(
        conn=conn,
        table='function_signatures',
        rows=function_signatures,
        upsert='do_update',
    )


async def async_select_function_signatures(
    conn: toolsql.SAConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
    id: int | None = None,
    bytes_signature: str | None = None,
) -> typing.Sequence[fourbyte_spec.Entry] | None:

    where_equals = {
        'id': id,
        'hex_signature': hex_signature,
        'text_signature': text_signature,
        'bytes_signature': bytes_signature,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    return toolsql.select(  # type: ignore
        conn=conn,
        table='function_signatures',
        where_equals=where_equals,
        raise_if_table_dne=False,
    )


async def async_delete_function_signatures(
    conn: toolsql.SAConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
) -> None:

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
        table='function_signatures',
        where_equals=where_equals,
    )


#
# # events
#


async def async_upsert_event_signature(
    event_signature: fourbyte_spec.PartialEntry,
    conn: toolsql.SAConnection,
) -> None:

    toolsql.insert(
        conn=conn,
        table='event_signatures',
        row=event_signature,
        upsert='do_update',
    )


async def async_upsert_event_signatures(
    event_signatures: typing.Sequence[fourbyte_spec.PartialEntry],
    conn: toolsql.SAConnection,
) -> None:

    toolsql.insert(
        conn=conn,
        table='event_signatures',
        rows=event_signatures,
        upsert='do_update',
    )


async def async_select_event_signatures(
    conn: toolsql.SAConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
    id: int | None = None,
    bytes_signature: str | None = None,
) -> typing.Sequence[fourbyte_spec.Entry] | None:

    where_equals = {
        'hex_signature': hex_signature,
        'text_signature': text_signature,
        'id': id,
        'bytes_signature': bytes_signature,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    return toolsql.select(  # type: ignore
        conn=conn,
        table='event_signatures',
        where_equals=where_equals,
        raise_if_table_dne=False,
    )


async def async_delete_event_signatures(
    conn: toolsql.SAConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
) -> None:

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
        table='event_signatures',
        where_equals=where_equals,
    )
