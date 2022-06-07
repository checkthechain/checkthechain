from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_block(
    block: spec.Block,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('blocks', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row=block,
        upsert='do_update',
    )


async def async_upsert_blocks(
    blocks: typing.Sequence[spec.Block],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('blocks', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=blocks,
        upsert='do_update',
    )


async def async_select_block(
    block_number: int | str,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> spec.Block | None:

    table = schema_utils.get_table_name('blocks', network=network)

    block = toolsql.select(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
        return_count='one',
        raise_if_table_dne=False,
    )

    if block is not None and block['base_fee_per_gas'] is None:
        del block['base_fee_per_gas']

    return block


async def async_select_blocks(
    block_numbers: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> typing.Sequence[spec.Block | None] | None:

    table = schema_utils.get_table_name('blocks', network=network)

    if block_numbers is not None:
        blocks = toolsql.select(
            conn=conn,
            table=table,
            where_in={'number': block_numbers},
            raise_if_table_dne=False,
        )

    elif start_block is not None and end_block is not None:
        blocks = toolsql.select(
            conn=conn,
            table=table,
            where_gte={'number': start_block},
            where_lte={'number': end_block},
            raise_if_table_dne=False,
        )
        block_numbers = range(start_block, end_block + 1)

    else:
        raise Exception(
            'must specify block_numbers or start_block and end_block'
        )

    if blocks is None:
        return None

    for block in blocks:
        if block is not None and block['base_fee_per_gas'] is None:
            del block['base_fee_per_gas']

    blocks_by_number = {
        block['number']: block for block in blocks if block is not None
    }

    return [blocks_by_number.get(number) for number in block_numbers]


async def async_delete_block(
    block_number: int | str,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('blocks', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
    )


async def async_delete_blocks(
    block_numbers: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('blocks', network=network)

    if block_numbers is not None:
        toolsql.delete(
            conn=conn,
            table=table,
            where_in={'number': block_numbers},
        )
    elif start_block is not None and end_block is not None:
        toolsql.delete(
            conn=conn,
            table=table,
            where_gte={'number': start_block},
            where_lte={'number': end_block},
        )
    else:
        raise Exception(
            'must specify block_numbrs or start_block and end_block'
        )


#
# # do not export these functions
#


async def async_select_block_timestamp(
    conn: toolsql.SAConnection,
    block_number: int,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('blocks', network=network)

    return toolsql.select(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
        row_format='only_column',
        only_columns=['timestamp'],
        return_count='one',
        raise_if_table_dne=False,
    )


async def async_select_block_timestamps(
    conn: toolsql.SAConnection,
    block_numbers: typing.Sequence[typing.SupportsInt],
    network: spec.NetworkReference | None = None,
) -> list[int | None]:

    table = schema_utils.get_table_name('blocks', network=network)

    block_numbers_int = [int(item) for item in block_numbers]

    results = toolsql.select(
        conn=conn,
        table=table,
        where_in={'number': block_numbers_int},
        raise_if_table_dne=False,
    )

    block_timestamps = {row['number']: row['timestamp'] for row in results}

    return [
        block_timestamps.get(block_number) for block_number in block_numbers
    ]


async def async_select_max_block_number(
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('blocks', network=network)
    result = toolsql.select(
        conn=conn,
        table=table,
        sql_functions=[
            ['max', 'number'],
        ],
        return_count='one',
        raise_if_table_dne=False,
    )
    return result['max__block_number']


async def async_select_max_block_timestamp(
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('blocks', network=network)
    result = toolsql.select(
        conn=conn,
        table=table,
        sql_functions=[
            ['max', 'timestamp'],
        ],
        return_count='one',
        raise_if_table_dne=False,
    )
    return result['max__timestamp']


__all__ = (
    'async_upsert_block',
    'async_upsert_blocks',
    'async_select_block',
    'async_select_blocks',
    'async_delete_block',
    'async_delete_blocks',
)
