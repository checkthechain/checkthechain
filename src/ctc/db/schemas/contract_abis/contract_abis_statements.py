from __future__ import annotations

import json
import typing

import toolsql

from ctc import spec
from ... import schema_utils


async def async_upsert_contract_abi(
    *,
    address: spec.Address,
    abi: spec.ContractABI,
    includes_proxy: bool,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    abi_text = json.dumps(abi)

    table = schema_utils.get_table_schema('contract_abis', context=context)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row={
            'address': address.lower(),
            'abi_text': abi_text,
            'includes_proxy': includes_proxy,
        },
        upsert=True,
    )


async def async_select_contract_abi(
    address: spec.Address,
    *,
    context: spec.Context = None,
    conn: toolsql.AsyncConnection,
) -> spec.ContractABI | None:

    table = schema_utils.get_table_schema(
        'contract_abis',
        context=context,
    )
    abi_text = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals={'address': address.lower()},
        columns=['abi_text'],
        output_format='cell_or_none',
    )
    if abi_text is not None:
        contract_abi: spec.ContractABI = json.loads(abi_text)
        return contract_abi
    else:
        return None


async def async_select_contract_abis(
    addresses: typing.Sequence[spec.Address] | None = None,
    *,
    context: spec.Context = None,
    conn: toolsql.AsyncConnection,
) -> typing.Mapping[spec.Address, spec.ContractABI] | None:

    table = schema_utils.get_table_schema(
        'contract_abis',
        context=context,
    )

    if addresses is not None:
        where_in = {'address': addresses}
    else:
        where_in = None
    results = await toolsql.async_select(
        conn=conn,
        table=table,
        where_in=where_in,
    )

    if results is None:
        return None

    return {
        result['address']: json.loads(result['abi_text']) for result in results
    }


async def async_delete_contract_abi(
    address: spec.Address,
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema(
        'contract_abis',
        context=context,
    )
    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'address': address.lower()},
    )

