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
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:
    table = schema_utils.get_table_schema('dex_pools', context=context)
    dex_pool = _format_dex_pool(dex_pool)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=dex_pool,
        upsert=True,
    )


async def async_upsert_dex_pools(
    *,
    dex_pools: typing.Sequence[spec.DexPool],
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:
    if len(dex_pools) == 0:
        return
    table = schema_utils.get_table_schema('dex_pools', context=context)
    dex_pools = [_format_dex_pool(dex_pool) for dex_pool in dex_pools]
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=dex_pools,
        upsert=True,
    )


async def async_upsert_dex_pool_factory_query(
    *,
    factory: spec.Address,
    last_scanned_block: int,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:
    table = schema_utils.get_table_schema(
        'dex_pool_factory_queries',
        context=context,
    )
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row={
            'factory': factory.lower(),
            'last_scanned_block': last_scanned_block,
        },
        upsert=True,
    )


async def async_delete_dex_pool(
    *,
    conn: toolsql.AsyncConnection,
    dex_pool: spec.Address,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('dex_pools', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'address': dex_pool.lower()},
    )


async def async_delete_dex_pools(
    *,
    conn: toolsql.AsyncConnection,
    dex_pools: typing.Sequence[spec.Address],
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('dex_pools', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_in={'address': [dex_pool.lower() for dex_pool in dex_pools]},
    )


async def async_delete_dex_pool_factory_query(
    *,
    conn: toolsql.AsyncConnection,
    factory: spec.Address,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema(
        'dex_pool_factory_queries', context=context
    )

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'factory': factory.lower()},
    )


async def async_select_dex_pool(
    address: spec.Address,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> spec.DexPool | None:

    table = schema_utils.get_table_schema('dex_pools', context=context)

    where_equals = {'address': address.lower()}

    result = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        output_format='single_dict_or_none',
    )
    return result  # type: ignore


async def async_select_dex_pools_by_id(
    addresses: typing.Sequence[spec.Address],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> typing.Mapping[spec.Address, spec.DexPool | None] | None:
    raise NotImplementedError()

    if len(addresses) == 0:
        return {}

    table = schema_utils.get_table_schema('dex_pools', context=context)

    results = await toolsql.async_select(
        conn=conn,
        table=table,
        where_in={'address': addresses},
    )

    results_by_address = {
        row['address']: row for row in results if row is not None
    }

    return {address: results_by_address.get(address) for address in addresses}


async def async_select_dex_pools(
    *,
    factory: spec.Address | None = None,
    factories: typing.Sequence[spec.Address] | None = None,
    assets: typing.Sequence[spec.Address] | None = None,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
    start_block: int | None = None,
    end_block: int | None = None,
) -> typing.Sequence[spec.DexPool] | None:

    table = schema_utils.get_table_schema('dex_pools', context=context)

    query: typing.MutableMapping[str, typing.Any] = {}
    if factory is not None:
        query.setdefault('where_equals', {})
        query['where_equals']['factory'] = factory
    if factories is not None:
        query.setdefault('where_in', {})
        query['where_in']['factory'] = factories
    if assets is not None:
        for asset in assets:
            asset = asset.lower()
            query['where_or'] = [
                {'where_equals': {'asset0': asset}},
                {'where_equals': {'asset1': asset}},
                {'where_equals': {'asset2': asset}},
                {'where_equals': {'asset3': asset}},
            ]
    if start_block is not None:
        query.setdefault('where_gte', {})
        query['where_gte']['creation_block'] = start_block
    if end_block is not None:
        query.setdefault('where_lte', {})
        query['where_lte']['creation_block'] = end_block

    return await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        **query,
    )


async def async_select_dex_pool_factory_last_scanned_block(
    factory: spec.Address,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> int | None:

    table = schema_utils.get_table_schema(
        'dex_pool_factory_queries', context=context
    )

    result = await toolsql.async_select(
        conn=conn,
        table=table,
        columns=['last_scanned_block'],
        output_format='cell_or_none',
        where_equals={'factory': factory.lower()},
    )

    if result is None or isinstance(result, int):
        return result
    else:
        raise Exception('bad data format received from db')

