from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    class BlockGasRow(TypedDict):
        block_number: int
        median_gas_fee: int | float | None
        timestamp: int


async def async_upsert_median_block_gas_fee(
    block_number: int,
    *,
    median_gas_fee: int | float | None,
    timestamp: int,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_gas', context=context)

    row = {
        'block_number': block_number,
        'median_gas_fee': median_gas_fee,
        'timestamp': timestamp,
    }
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=row,
        upsert=True,
    )


async def async_upsert_median_blocks_gas_fees(
    block_gas_data: typing.Sequence[BlockGasRow],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_gas', context=context)

    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=block_gas_data,
        upsert=True,
    )


async def async_select_median_block_gas_fee(
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> BlockGasRow | None:

    table = schema_utils.get_table_schema('block_gas', context=context)

    result: BlockGasRow = await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        output_format='single_dict_or_none',
    )
    return result


async def async_select_median_blocks_gas_fees(
    block_numbers: typing.Sequence[int],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> typing.Mapping[int, BlockGasRow] | None:

    table = schema_utils.get_table_schema('block_gas', context=context)

    results = await toolsql.async_select(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
    )
    if results is None:
        return None
    else:
        return {result['block_number']: result for result in results}  # type: ignore


async def async_delete_block_gas(
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_gas', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
    )


async def async_delete_blocks_gasses(
    block_numbers: typing.Sequence[int],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('block_gas', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
    )
