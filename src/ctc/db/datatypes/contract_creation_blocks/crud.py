from __future__ import annotations

import toolsql

from ctc import spec
from ... import schema_utils


def set_contract_creation_block(
    conn: toolsql.SAConnection,
    address: spec.Address,
    block_number: int,
    network: spec.NetworkReference | None = None,
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


def get_contract_creation_block(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
) -> int | None:

    table = schema_utils.get_table_name(
        'contract_creation_blocks',
        network=network,
    )
    return toolsql.select(
        conn=conn,
        table=table,
        row_id=address.lower(),
        return_count='one',
        only_columns=['block_number'],
        row_format='only_column',
    )


def delete_contract_creation_block(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
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

