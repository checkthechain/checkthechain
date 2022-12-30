from __future__ import annotations

import asyncio
import typing

import toolsql

from ctc import config
from ctc import spec
from ... import schema_utils


async def async_upsert_erc20_metadata(
    *,
    context: spec.Context,
    address: spec.Address,
    symbol: str | None = None,
    decimals: int | None = None,
    name: str | None = None,
    upsert: bool = True,
    conn: toolsql.SAConnection,
) -> None:

    # construct row
    row = {
        'address': address.lower(),
        'symbol': symbol,
        'decimals': decimals,
        'name': name,
    }
    row = {k: v for k, v in row.items() if v is not None}

    # get upsert option
    if upsert:
        upsert_option: toolsql.ConflictOption | None = 'do_update'
    else:
        upsert_option = None

    # get table name
    table = schema_utils.get_table_name('erc20_metadata', context=context)

    # insert data
    toolsql.insert(
        conn=conn,
        table=table,
        row=row,
        upsert=upsert_option,
    )


async def async_upsert_erc20s_metadata(
    *,
    erc20s_metadata: typing.Sequence[spec.ERC20Metadata],
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:
    coroutines = [
        async_upsert_erc20_metadata(conn=conn, context=context, **metadata)
        for metadata in erc20s_metadata
    ]
    await asyncio.gather(*coroutines)


async def async_select_erc20_metadata(
    address: spec.Address | None = None,
    *,
    symbol: str | None = None,
    case_insensitive_symbol: bool = False,
    context: spec.Context | None = None,
    conn: toolsql.SAConnection,
) -> spec.ERC20Metadata | None:

    table = schema_utils.get_table_name('erc20_metadata', context=context)

    if address is not None:
        query: typing.Mapping[str, typing.Any] = {'row_id': address.lower()}
    elif symbol is not None:
        if case_insensitive_symbol:
            query = {'where_ilike': {'symbol': symbol}}
        else:
            query = {'where_equals': {'symbol': symbol}}
    else:
        raise Exception('must specify address or symbol')

    erc20_metadata: spec.ERC20Metadata = toolsql.select(
        conn=conn,
        table=table,
        row_count='at_most_one',
        row_format='dict',
        return_count='one',
        raise_if_table_dne=False,
        **query,
    )

    return erc20_metadata


async def async_select_erc20s_metadata(
    addresses: typing.Sequence[spec.Address],
    *,
    context: spec.Context | None = None,
    conn: toolsql.SAConnection,
) -> typing.Sequence[spec.ERC20Metadata | None] | None:

    table = schema_utils.get_table_name('erc20_metadata', context=context)
    results = toolsql.select(
        conn=conn,
        table=table,
        row_ids=[address.lower() for address in addresses],
        raise_if_table_dne=False,
    )

    if results is None:
        return None

    # package into output
    results_by_address = {result['address']: result for result in results}

    return [results_by_address.get(address) for address in addresses]


async def async_delete_erc20_metadata(
    address: spec.Address,
    *,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:
    table = schema_utils.get_table_name('erc20_metadata', context=context)
    toolsql.delete(table=table, conn=conn, row_id=address.lower())


async def async_delete_erc20s_metadata(
    addresses: typing.Sequence[spec.Address],
    *,
    context: spec.Context,
    conn: toolsql.SAConnection,
) -> None:
    table = schema_utils.get_table_name('erc20_metadata', context=context)
    toolsql.delete(
        table=table,
        conn=conn,
        row_ids=[address.lower() for address in addresses],
    )

