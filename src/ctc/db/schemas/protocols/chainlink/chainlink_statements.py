from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils
from . import chainlink_schema_defs


async def async_upsert_chainlink_feed(
    feed: dict,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('oracle_feeds', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row=feed,
        upsert='do_update',
    )


async def async_upsert_chainlink_feeds(
    feeds: typing.List[typing.Mapping[str, typing.Any]],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('oracle_feeds', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=feeds,
        upsert='do_update',
    )


async def async_select_chainlink_feed(
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    address: spec.Address | None = None,
    name: str | None = None,
    asset: str | None = None,
) -> chainlink_schema_defs.ChainlinkFeed:
    table = schema_utils.get_table_name('block_timestamps', network=network)

    where_equals = {
        'address': address,
        'name': name,
        'asset': asset,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    return toolsql.select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        return_count='one',
        raise_if_table_dne=False,
    )


async def async_delete_chainlink_feed(
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    address: spec.Address | None = None,
    name: str | None = None,
    asset: str | None = None,
) -> None:

    where_equals = {
        'address': address,
        'name': name,
        'asset': asset,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }
    if len(where_equals) == 0:
        raise Exception('must specify which feeds to delete')

    table = schema_utils.get_table_name('chainlink_feed', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals=where_equals,
    )
