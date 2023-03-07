from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_contract_creation_block(
    *,
    address: spec.Address,
    block_number: int,
    context: spec.Context = None,
    conn: toolsql.AsyncConnection,
) -> None:

    table = schema_utils.get_table_schema(
        'contract_creation_blocks', context=context
    )
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row={
            'address': address.lower(),
            'block_number': block_number,
        },
        upsert=True,
    )


async def async_select_contract_creation_block(
    address: spec.Address,
    *,
    context: spec.Context = None,
    conn: toolsql.AsyncConnection,
) -> int | None:

    table = schema_utils.get_table_schema(
        'contract_creation_blocks',
        context=context,
    )
    result = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals={'address': address.lower()},
        columns=['block_number'],
        output_format='cell_or_none',
    )

    if result is not None and not isinstance(result, int):
        raise Exception('invalid db result')

    return result


async def async_select_contract_creation_blocks(
    *,
    context: spec.Context = None,
    conn: toolsql.AsyncConnection,
) -> typing.Sequence[typing.Mapping[str, typing.Any]] | None:
    table = schema_utils.get_table_schema(
        'contract_creation_blocks',
        context=context,
    )
    result: typing.Sequence[typing.Mapping[str, typing.Any]] | None
    result = await toolsql.async_select(conn=conn, table=table)

    return result


async def async_delete_contract_creation_block(
    address: spec.Address,
    *,
    context: spec.Context = None,
    conn: toolsql.AsyncConnection,
) -> None:
    table = schema_utils.get_table_schema(
        'contract_creation_blocks',
        context=context,
    )
    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'address': address.lower()},
    )

