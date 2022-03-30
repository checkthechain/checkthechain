from __future__ import annotations

import typing

import toolsql

from ctc import spec
from ... import db_spec
from ... import schema_utils


def insert_erc20_metadata(
    conn: toolsql.SAConnection,
    address: spec.Address,
    symbol: str | None = None,
    decimals: int | None = None,
    upsert: bool = True,
    network: spec.NetworkReference | None = None,
) -> None:

    # construct row
    row = {
        'address': address.lower(),
        'symbol': symbol,
        'decimals': decimals,
    }
    row = {k: v for k, v in row.items() if v is not None}

    # get upsert option
    if upsert:
        upsert_option: toolsql.ConflictOption | None = 'do_update'
    else:
        upsert_option = None

    # get table name
    table = schema_utils.get_network_table_name(
        table_name='erc20_metadata',
        network=network,
    )

    # insert data
    toolsql.insert(
        conn=conn,
        table=table,
        row=row,
        upsert=upsert_option,
    )


def insert_erc20s_metadatas(
    conn: toolsql.SAConnection,
    metadatas: typing.Sequence[db_spec.ERC20Metadata],
    network: spec.NetworkReference | None = None,
) -> None:
    for metadata in metadatas:
        insert_erc20_metadata(conn=conn, network=network, **metadata)


def select_erc20_metadata(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
) -> db_spec.ERC20Metadata | None:
    table = schema_utils.get_network_table_name(
        table_name='erc20_metadata',
        network=network,
    )
    return toolsql.select(
        conn=conn,
        table=table,
        row_id=address.lower(),
        row_count='at_most_one',
        row_format='dict',
        return_count='one',
    )


def select_erc20s_metadatas(
    conn: toolsql.SAConnection,
    addresses: typing.Sequence[spec.Address],
    network: spec.NetworkReference | None = None,
) -> typing.Sequence[db_spec.ERC20Metadata]:
    table = schema_utils.get_network_table_name(
        table_name='erc20_metadata',
        network=network,
    )
    return toolsql.select(
        conn=conn,
        table=table,
        row_ids=[address.lower() for address in addresses],
    )


def delete_erc20_metadata(
    conn: toolsql.SAConnection,
    address: spec.Address,
    network: spec.NetworkReference | None = None,
) -> None:
    table = schema_utils.get_network_table_name(
        network=network,
        table_name='erc20_metadata',
    )
    toolsql.delete(table=table, conn=conn, row_id=address)


def delete_erc20s_metadata(
    conn: toolsql.SAConnection,
    addresses: typing.Sequence[spec.Address],
    network: spec.NetworkReference | None = None,
) -> None:
    table = schema_utils.get_network_table_name(
        network=network,
        table_name='erc20_metadata',
    )
    toolsql.delete(table=table, conn=conn, row_ids=addresses)

