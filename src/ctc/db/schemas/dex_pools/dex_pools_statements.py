from __future__ import annotations

import copy
import typing

import toolsql

from ctc import spec
from ... import schema_utils


def _format_dex_pool(dex_pool: spec.DexPool) -> spec.DexPool:
    formatted = copy.copy(dex_pool)
    return formatted


async def async_upsert_dex_pool(
    *,
    dex_pool: spec.DexPool,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    table = schema_utils.get_table_name('dex_pools', network=network)
    dex_pool = _format_dex_pool(dex_pool)
    toolsql.insert(
        conn=conn,
        table=table,
        row=dex_pool,
        upsert='do_update',
    )


async def async_upsert_dex_pools(
    *,
    dex_pools: typing.Sequence[spec.DexPool],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    table = schema_utils.get_table_name('dex_pools', network=network)
    dex_pools = [_format_dex_pool(dex_pool) for dex_pool in dex_pools]
    toolsql.insert(
        conn=conn,
        table=table,
        rows=dex_pools,
        upsert='do_update',
    )


async def async_upsert_dex_pool_factory_query(
    *,
    factory: spec.Address,
    last_scanned_block: int,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    table = schema_utils.get_table_name(
        'dex_pool_factory_queries',
        network=network,
    )
    toolsql.insert(
        conn=conn,
        table=table,
        row={
            'factory': factory.lower(),
            'last_scanned_block': last_scanned_block,
        },
        upsert='do_update',
    )


async def async_delete_dex_pool(
    *,
    conn: toolsql.SAConnection,
    dex_pool: spec.Address,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('dex_pools', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'address': dex_pool.lower()},
    )


async def async_delete_dex_pools(
    *,
    conn: toolsql.SAConnection,
    dex_pools: typing.Sequence[spec.Address],
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('dex_pools', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_in={'address': [dex_pool.lower() for dex_pool in dex_pools]},
    )


async def async_delete_dex_pool_factory_query(
    *,
    conn: toolsql.SAConnection,
    factory: spec.Address,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name(
        'dex_pool_factory_queries', network=network
    )

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'factory': factory.lower()},
    )


async def async_select_dex_pool(
    address: spec.Address,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> spec.DexPool | None:

    table = schema_utils.get_table_name('dex_pools', network=network)

    where_equals = {'address': address.lower()}

    result = toolsql.select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        return_count='one',
        raise_if_table_dne=False,
    )
    return result  # type: ignore


async def async_select_dex_pools_by_id(
    addresses: typing.Sequence[spec.Address],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> typing.Mapping[spec.Address, spec.DexPool | None] | None:
    raise NotImplementedError()

    if len(addresses) == 0:
        return {}

    table = schema_utils.get_table_name('dex_pools', network=network)

    results = await toolsql.select(
        conn=conn,
        table=table,
        raise_if_table_dne=False,
        where_in={'address': addresses},
    )

    results_by_address = {
        row['address']: row for row in results if row is not None
    }

    return {address: results_by_address.get(address) for address in addresses}


async def async_select_dex_pools(
    *,
    factory: spec.Address | None = None,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> typing.Sequence[spec.DexPool] | None:
    """

    wanted args:
    - n_assets: specify number of assets in pool
        - must specify that certain columns are None
    - has_assets: specify assets that are contained in pool
        - must specify that one of the asset columns equals the asset
        - need an "or" query
    """

    table = schema_utils.get_table_name('dex_pools', network=network)

    query: typing.MutableMapping[str, typing.Any] = {}
    if factory is not None:
        query.setdefault('where_equals', {})
        query['where_equals']['factory'] = factory

    return toolsql.select(  # type: ignore
        conn=conn, table=table, raise_if_table_dne=False, **query
    )


async def async_select_dex_pool_factory_last_scanned_block(
    factory: spec.Address,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> int | None:

    table = schema_utils.get_table_name(
        'dex_pool_factory_queries', network=network
    )

    result = toolsql.select(
        conn=conn,
        table=table,
        raise_if_table_dne=False,
        row_format='only_column',
        only_columns=['last_scanned_block'],
        return_count='one',
        where_equals={'factory': factory.lower()},
    )

    if result is None or isinstance(result, int):
        return result
    else:
        raise Exception('bad data format received from db')
