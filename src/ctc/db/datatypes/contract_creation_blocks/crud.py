from __future__ import annotations

import toolsql

from ctc import spec
from ... import schema_utils


def set_contract_creation_block(
    conn: toolsql.SAConnection,
    address: spec.Address,
    block: int,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name(
        'contract_creation_blocks', network=network
    )
    toolsql.insert(
        conn=conn,
        table=table,
        row={'address': address.lower(), 'block': block},
        upsert='do_update',
    )


def get_contract_creation_block(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
) -> int:

    table = schema_utils.get_table_name(
        'contract_creation_blocks', network=network,
    )
    return toolsql.select(
        conn=conn,
        table=table,
        row_id=address.lower(),
        return_count='one',
        upsert='do_update',
        only_columns='block',
        row_format='only_column',
    )

