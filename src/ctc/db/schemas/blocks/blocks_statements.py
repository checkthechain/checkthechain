from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


def _remove_block_transactions(block: spec.Block) -> spec.Block:
    txs = block['transactions']
    if len(txs) > 0 and isinstance(txs[0], dict):
        if typing.TYPE_CHECKING:
            full_txs = typing.cast(list[spec.Transaction], txs)
        else:
            full_txs = txs
        tx_hashes = [tx['hash'] for tx in full_txs]
        return dict(block, transactions=tx_hashes)  # type: ignore
    else:
        return block


async def async_upsert_block(
    *,
    block: spec.Block,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('blocks', network=network)
    block = _remove_block_transactions(block)
    toolsql.insert(
        conn=conn,
        table=table,
        row=block,
        upsert='do_update',
    )


async def async_upsert_blocks(
    *,
    blocks: typing.Sequence[spec.Block],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('blocks', network=network)
    blocks = [_remove_block_transactions(block) for block in blocks]
    toolsql.insert(
        conn=conn,
        table=table,
        rows=blocks,
        upsert='do_update',
    )


async def async_select_block(
    block_number: int | str,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> spec.Block | None:

    table = schema_utils.get_table_name('blocks', network=network)

    block: spec.Block | None = toolsql.select(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
        return_count='one',
        raise_if_table_dne=False,
    )

    if block is not None and block['base_fee_per_gas'] is None:
        del block['base_fee_per_gas']
    else:
        if block is not None and block['base_fee_per_gas'] is not None:
            block['base_fee_per_gas'] = int(block['base_fee_per_gas'])

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
        else:
            block['base_fee_per_gas'] = int(block['base_fee_per_gas'])

    blocks_by_number = {
        block['number']: block for block in blocks if block is not None
    }

    return [blocks_by_number.get(number) for number in block_numbers]


async def async_delete_block(
    block_number: int | str,
    *,
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
    block_number: int,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name('blocks', network=network)

    result = toolsql.select(
        conn=conn,
        table=table,
        where_equals={'number': block_number},
        row_format='only_column',
        only_columns=['timestamp'],
        return_count='one',
        raise_if_table_dne=False,
    )
    if result is not None and not isinstance(result, int):
        raise Exception('invalid db result')
    return result


async def async_select_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> list[int | None] | None:

    table = schema_utils.get_table_name('blocks', network=network)

    block_numbers_int = [int(item) for item in block_numbers]

    results = toolsql.select(
        conn=conn,
        table=table,
        where_in={'number': block_numbers_int},
        raise_if_table_dne=False,
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
    if result is not None:
        output = result['max__block_number']
        if output is not None and not isinstance(output, int):
            raise Exception('invalid db result')
        return output
    else:
        return None


async def async_select_max_block_timestamp(
    *,
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
