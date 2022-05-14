from __future__ import annotations

import json

import toolsql

from ctc import spec
from .. import db_schemas


async def async_store_contract_abi(
    address: spec.Address,
    abi: spec.ContractABI,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    abi_text = json.dumps(abi)

    table = db_schemas.get_table_name(
        'contract_abis', network=network
    )
    toolsql.insert(
        conn=conn,
        table=table,
        row={
            'address': address.lower(),
            'abi_text': abi_text,
        },
        upsert='do_update',
    )


async def async_select_contract_abi(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
) -> spec.ContractABI | None:

    table = db_schemas.get_table_name(
        'contract_abis',
        network=network,
    )
    abi_text = toolsql.select(
        conn=conn,
        table=table,
        row_id=address.lower(),
        return_count='one',
        only_columns=['abi_text'],
        row_format='only_column',
    )
    if abi_text is not None:
        return json.loads(abi_text)
    else:
        return None


async def async_delete_contract_abi(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
) -> None:
    table = db_schemas.get_table_name(
        'contract_abis',
        network=network,
    )
    toolsql.delete(
        conn=conn,
        table=table,
        row_id=address.lower(),
    )
