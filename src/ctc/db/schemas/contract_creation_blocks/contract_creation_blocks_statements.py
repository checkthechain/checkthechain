from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_contract_creation_block(
    *,
    address: spec.Address,
    block_number: int,
    network: spec.NetworkReference | None = None,
    conn: toolsql.SAConnection,
) -> None:

    table = schema_utils.get_table_name(
        'contract_creation_blocks', network=network
    )
    toolsql.insert(
        conn=conn,
        table=table,
        row={
            'address': address.lower(),
            'block_number': block_number,
        },
        upsert='do_update',
    )


async def async_select_contract_creation_block(
    address: spec.Address,
    *,
    network: spec.NetworkReference | None = None,
    conn: toolsql.SAConnection,
) -> int | None:

    table = schema_utils.get_table_name(
        'contract_creation_blocks',
        network=network,
    )
    result = toolsql.select(
        conn=conn,
        table=table,
        row_id=address.lower(),
        return_count='one',
        only_columns=['block_number'],
        row_format='only_column',
        raise_if_table_dne=False,
    )

    if result is not None and not isinstance(result, int):
        raise Exception('invalid db result')

    return result


async def async_select_contract_creation_blocks(
    *,
    network: spec.NetworkReference | None = None,
    conn: toolsql.SAConnection,
) -> typing.Sequence[typing.Mapping[str, typing.Any]] | None:
    table = schema_utils.get_table_name(
        'contract_creation_blocks',
        network=network,
    )
    result: typing.Sequence[
        typing.Mapping[str, typing.Any]
    ] | None = toolsql.select(
        conn=conn,
        table=table,
        raise_if_table_dne=False,
    )
    return result


async def async_delete_contract_creation_block(
    address: spec.Address,
    *,
    network: spec.NetworkReference | None = None,
    conn: toolsql.SAConnection,
) -> None:
    table = schema_utils.get_table_name(
        'contract_creation_blocks',
        network=network,
    )
    toolsql.delete(
        conn=conn,
        table=table,
        row_id=address.lower(),
    )
