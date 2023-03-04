from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


def _prepare_block_for_db(
    block: spec.DBBlock,
) -> typing.Mapping[str, typing.Any]:

    # remove extra keys
    extra_keys = ['send_root', 'l1_block_number', 'send_count', 'transactions']
    if any(key in block for key in extra_keys):
        block = block.copy()
        for key in extra_keys:
            if key in block:
                del block[key]  # type: ignore
    return block


async def async_upsert_block(
    *,
    block: spec.DBBlock,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema('blocks', context=context)
    ready_block = _prepare_block_for_db(block)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=ready_block,
        upsert=True,
    )


async def async_upsert_blocks(
    *,
    blocks: typing.Sequence[spec.DBBlock],
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema('blocks', context=context)
    ready_blocks = [_prepare_block_for_db(block) for block in blocks]
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=ready_blocks,
        upsert=True,
    )


async def async_select_block(
    block_number: int | str,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> spec.DBBlock | None:

    table = schema_utils.get_table_schema('blocks', context=context)

    block: spec.DBBlock | None = await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        where_equals={'number': block_number},
        output_format='single_dict_or_none',
    )

    return block


async def async_select_blocks(
    block_numbers: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> typing.Sequence[spec.DBBlock | None] | None:

    table = schema_utils.get_table_schema('blocks', context=context)

    if block_numbers is not None:
        blocks = await toolsql.async_select(
            conn=conn,
            table=table,
            where_in={'number': block_numbers},
        )

    elif start_block is not None and end_block is not None:
        blocks = await toolsql.async_select(
            conn=conn,
            table=table,
            where_gte={'number': start_block},
            where_lte={'number': end_block},
        )
        block_numbers = range(start_block, end_block + 1)

    else:
        raise Exception(
            'must specify block_numbers or start_block and end_block'
        )

    if blocks is None:
        return None

    for block in blocks:
        if block is not None and block['base_fee_per_gas'] is not None:
            block['base_fee_per_gas'] = int(block['base_fee_per_gas'])

    blocks_by_number = {
        block['number']: block for block in blocks if block is not None
    }

    return [blocks_by_number.get(number) for number in block_numbers]  # type: ignore


async def async_delete_block(
    block_number: int | str,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema('blocks', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
    )


async def async_delete_blocks(
    block_numbers: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    table = schema_utils.get_table_schema('blocks', context=context)

    if block_numbers is not None:
        await toolsql.async_delete(
            conn=conn,
            table=table,
            where_in={'number': block_numbers},
        )
    elif start_block is not None and end_block is not None:
        await toolsql.async_delete(
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
    block_number: int,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    table = schema_utils.get_table_schema('blocks', context=context)

    result = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
        columns=['timestamp'],
        output_format='cell_or_none',
    )
    if result is not None and not isinstance(result, int):
        raise Exception('invalid db result')
    return result


async def async_select_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> list[int | None] | None:

    table = schema_utils.get_table_schema('blocks', context=context)

    block_numbers_int = [int(item) for item in block_numbers]

    results = await toolsql.async_select(
        conn=conn,
        table=table,
        where_in={'number': block_numbers_int},
    )

    if results is None:
        return None

    block_timestamps = {
        row['number']: row['timestamp'] for row in results if row is not None
    }

    return [
        block_timestamps.get(block_number) for block_number in block_numbers
    ]


async def async_select_max_block_number(
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    table = schema_utils.get_table_schema('blocks', context=context)
    result = await toolsql.async_select(
        conn=conn,
        table=table,
        columns=['max(number)'],
        output_format='cell',
    )
    if result is not None:
        output = result['max__block_number']
        if output is not None and not isinstance(output, int):
            raise Exception('invalid db result')
        return output
    else:
        return None


async def async_select_max_block_timestamp(
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> int | None:

    table = schema_utils.get_table_schema('blocks', context=context)
    result = await toolsql.async_select(
        conn=conn,
        table=table,
        columns=['max(number)'],
        output_format='cell',
    )
    if result is None:
        return None
    else:
        max_timestamp = result['max__timestamp']
        if max_timestamp is not None and not isinstance(max_timestamp, int):
            raise Exception('invalid db output')
        return max_timestamp


__all__ = (
    'async_upsert_block',
    'async_upsert_blocks',
    'async_select_block',
    'async_select_blocks',
    'async_delete_block',
    'async_delete_blocks',
)

