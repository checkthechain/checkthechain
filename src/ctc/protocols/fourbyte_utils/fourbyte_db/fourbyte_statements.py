from __future__ import annotations

import typing

import toolsql

from ctc import db
from ctc import spec
from .. import fourbyte_spec


#
# # functions
#


async def async_upsert_function_signature(
    function_signature: fourbyte_spec.PartialEntry,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:
    table = db.get_table_schema('function_signatures', context=None)

    function_signature = function_signature.copy()
    if 'bytes_signature' in function_signature:
        del function_signature['bytes_signature']

    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=function_signature,
        upsert=True,
    )


async def async_upsert_function_signatures(
    function_signatures: typing.Sequence[fourbyte_spec.PartialEntry],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:
    table = db.get_table_schema('function_signatures', context=None)

    function_signatures = []
    for function_signature in list(function_signatures):
        function_signature = function_signature.copy()
        del function_signature['bytes_signature']
        function_signatures.append(function_signature)

    if len(function_signatures) == 0:
        return
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=function_signatures,
        upsert=True,
    )


async def async_select_function_signatures(
    conn: toolsql.AsyncConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
    id: int | None = None,
    # bytes_signature: str | None = None,
    context: spec.Context = None,
) -> typing.Sequence[fourbyte_spec.Entry] | None:
    where_equals = {
        'id': id,
        'hex_signature': hex_signature,
        'text_signature': text_signature,
        # 'bytes_signature': bytes_signature,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    table = db.get_table_schema('function_signatures', context=None)

    return await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        where_equals=where_equals,
    )


async def async_delete_function_signatures(
    conn: toolsql.AsyncConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
    context: spec.Context = None,
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

    table = db.get_table_schema('function_signatures', context=None)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals=where_equals,
    )


#
# # events
#


async def async_upsert_event_signature(
    event_signature: fourbyte_spec.PartialEntry,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:
    table = db.get_table_schema('event_signatures', context=None)

    event_signature = event_signature.copy()
    if 'bytes_signature' in event_signature:
        del event_signature['bytes_signature']

    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=event_signature,
        upsert=True,
    )


async def async_upsert_event_signatures(
    event_signatures: typing.Sequence[fourbyte_spec.PartialEntry],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:
    table = db.get_table_schema('event_signatures', context=None)

    event_signatures = []
    for event_signature in list(event_signatures):
        event_signature = event_signature.copy()
        del event_signature['bytes_signature']
        event_signatures.append(event_signature)

    if len(event_signatures) == 0:
        return
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=event_signatures,
        upsert=True,
    )


async def async_select_event_signatures(
    conn: toolsql.AsyncConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
    id: int | None = None,
    # bytes_signature: str | None = None,
    context: spec.Context = None,
) -> typing.Sequence[fourbyte_spec.Entry] | None:
    where_equals = {
        'hex_signature': hex_signature,
        'text_signature': text_signature,
        'id': id,
        # 'bytes_signature': bytes_signature,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    table = db.get_table_schema('event_signatures', context=None)

    return await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        where_equals=where_equals,
    )


async def async_delete_event_signatures(
    conn: toolsql.AsyncConnection,
    *,
    hex_signature: str | None = None,
    text_signature: str | None = None,
    context: spec.Context = None,
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

    table = db.get_table_schema('event_signatures', context=None)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals=where_equals,
    )

