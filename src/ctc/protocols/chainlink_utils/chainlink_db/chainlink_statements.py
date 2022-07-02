from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ctc import db
from . import chainlink_schema_defs


async def async_upsert_feed(
    feed: typing.Mapping[typing.Any, typing.Any],
    conn: toolsql.SAConnection,
    *,
    network: spec.NetworkReference | None = None,
) -> None:

    feed = dict(feed, address=feed['address'].lower())

    table = db.get_table_name('chainlink_feeds', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row=feed,
        upsert='do_update',
    )


async def async_upsert_feeds(
    feeds: typing.Sequence[typing.Mapping[str, typing.Any]],
    conn: toolsql.SAConnection,
    *,
    network: spec.NetworkReference | None = None,
) -> None:

    feeds = [dict(feed, address=feed['address'].lower()) for feed in feeds]

    table = db.get_table_name('chainlink_feeds', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=feeds,
        upsert='do_update',
    )


async def async_select_feed(
    *,
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    address: spec.Address | None = None,
    name: str | None = None,
    asset: str | None = None,
) -> chainlink_schema_defs.ChainlinkFeed | None:
    table = db.get_table_name('chainlink_feeds', network=network)

    where_equals = {
        'address': address,
        'name': name,
        'asset': asset,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    return toolsql.select(  # type: ignore
        conn=conn,
        table=table,
        where_equals=where_equals,
        return_count='one',
        raise_if_table_dne=False,
    )


async def async_select_feeds(
    *,
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    address: spec.Address | None = None,
    name: str | None = None,
    asset: str | None = None,
    addresses: typing.Sequence[str] | None = None,
) -> typing.Sequence[chainlink_schema_defs.ChainlinkFeed | None] | None:

    table = db.get_table_name('chainlink_feeds', network=network)

    where_equals = {
        'address': address,
        'name': name,
        'asset': asset,
    }
    where_equals = {
        key: value for key, value in where_equals.items() if value is not None
    }

    if addresses is not None:
        where_in = {'address': addresses}
    else:
        where_in = None

    result = toolsql.select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        where_in=where_in,
        raise_if_table_dne=False,
    )

    return result  # type: ignore


async def async_delete_feed(
    network: spec.NetworkReference | None,
    conn: toolsql.SAConnection,
    *,
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

    table = db.get_table_name('chainlink_feeds', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals=where_equals,
    )
