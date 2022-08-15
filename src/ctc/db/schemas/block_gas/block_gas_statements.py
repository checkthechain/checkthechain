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
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('block_gas', network=network)

    row = {
        'block_number': block_number,
        'median_gas_fee': median_gas_fee,
        'timestamp': timestamp,
    }
    toolsql.insert(
        conn=conn,
        table=table,
        row=row,
        upsert='do_update',
    )


async def async_upsert_median_blocks_gas_fees(
    block_gas_data: typing.Sequence[BlockGasRow],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('block_gas', network=network)

    toolsql.insert(
        conn=conn,
        table=table,
        rows=block_gas_data,
        upsert='do_update',
    )


async def async_select_median_block_gas_fee(
    block_number: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> BlockGasRow | None:

    table = schema_utils.get_table_name('block_gas', network=network)

    result: BlockGasRow = toolsql.select(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
        return_count='one',
        raise_if_table_dne=False,
    )
    return result


async def async_select_median_blocks_gas_fees(
    block_numbers: typing.Sequence[int],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> typing.Mapping[int, BlockGasRow] | None:

    table = schema_utils.get_table_name('block_gas', network=network)

    results = toolsql.select(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
        raise_if_table_dne=False,
    )
    if results is None:
        return None
    else:
        return {result['block_number']: result for result in results}


async def async_delete_block_gas(
    block_number: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('block_gas', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'block_number': block_number},
    )


async def async_delete_blocks_gasses(
    block_numbers: typing.Sequence[int],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('block_gas', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_in={'block_number': block_numbers},
    )
