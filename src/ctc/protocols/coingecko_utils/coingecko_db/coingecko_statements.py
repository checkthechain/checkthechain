from __future__ import annotations

import typing

import toolsql

from ctc import spec
from . import coingecko_schema_defs


async def async_upsert_tokens(
    *,
    tokens: typing.Sequence[coingecko_schema_defs.CoingeckoToken],
    conn: toolsql.SAConnection,
    context: spec.Context = None,
) -> None:

    if len(tokens) == 0:
        return

    toolsql.insert(
        conn=conn,
        table='coingecko_tokens',
        rows=tokens,
        upsert='do_update',
    )


async def async_delete_tokens(
    *,
    ids: typing.Sequence[str],
    conn: toolsql.SAConnection,
    context: spec.Context = None,
) -> None:

    if len(ids) == 0:
        return

    toolsql.delete(
        conn=conn,
        table='coingecko_tokens',
        where_in={'id': ids},
    )


async def async_select_token(
    *,
    conn: toolsql.SAConnection,
    id: str | None = None,
    context: spec.Context = None,
) -> coingecko_schema_defs.CoingeckoToken | None:

    if id is not None:
        where_equals = {'id': id}
    else:
        raise Exception('must specify id')

    result: coingecko_schema_defs.CoingeckoToken = toolsql.select(
        conn=conn,
        table='coingecko_tokens',
        where_equals=where_equals,
        return_count='one',
        raise_if_table_dne=False,
    )

    return result


async def async_select_tokens(
    *,
    symbol_query: str | None = None,
    name_query: str | None = None,
    conn: toolsql.SAConnection,
    context: spec.Context = None,
) -> typing.Sequence[coingecko_schema_defs.CoingeckoToken] | None:

    # symbol query
    if symbol_query is not None:
        symbol_filter = {
            'where_ilike': {'symbol': {'%' + symbol_query.lower() + '%'}}
        }
    else:
        symbol_filter = None

    # name query
    if name_query is not None:
        name_filter = {
            'where_ilike': {'symbol': {'%' + name_query.lower() + '%'}}
        }
    else:
        name_filter = None

    # combine filters
    if symbol_filter is not None and name_filter is not None:
        select_kwargs = {'where_or': [symbol_filter, name_filter]}
    elif symbol_filter is not None:
        select_kwargs = symbol_filter
    elif name_filter is not None:
        select_kwargs = name_filter
    else:
        select_kwargs = {}

    result: typing.Sequence[
        coingecko_schema_defs.CoingeckoToken
    ] = toolsql.select(
        conn=conn,
        table='coingecko_tokens',
        raise_if_table_dne=False,
        order_by='market_cap_rank',
        **select_kwargs,
    )

    ranked: list[coingecko_schema_defs.CoingeckoToken] = []
    unranked: list[coingecko_schema_defs.CoingeckoToken] = []
    for item in result:
        if item['market_cap_rank'] is not None:
            ranked.append(item)
        else:
            unranked.append(item)

    together: typing.MutableSequence[coingecko_schema_defs.CoingeckoToken] = (
        ranked + unranked
    )

    return together

