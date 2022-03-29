from __future__ import annotations

import toolsql


def insert_erc20_metadata(
    conn, address, symbol=None, decimals=None, upsert=True
):
    row = {
        'address': address,
        'symbol': symbol,
        'decimals': decimals,
    }
    row = {k: v for k, v in row.items() if v is not None}

    if upsert:
        upsert_option = 'do_update'
    else:
        upsert_option = None

    toolsql.insert(
        conn=conn,
        table='erc20_metadata',
        row=row,
        upsert=upsert_option,
    )


def insert_erc20s_metadata(conn, metadatas):
    for metadata in metadatas:
        insert_erc20_metadata(conn, **metadata)


def update_erc20_metadata(conn, metadata, address, values):
    toolsql.update(
        conn=conn,
        table='erc20_metadata',
        row_id=address,
        update_values=values,
    )


def select_erc20_metadata(conn, address, **select_kwargs):
    return toolsql.select(
        conn=conn,
        table='erc20_metadata',
        row_id=address,
        row_count='at_most_one',
        return_count='one',
        **select_kwargs,
    )


def select_erc20s_metadatas(conn, addresses=None, **select_kwargs):
    return toolsql.select(
        conn=conn,
        table='erc20_metadata',
        row_ids=addresses,
        **select_kwargs,
    )


def delete_erc20_metadata(conn, address):
    toolsql.delete(table='erc20_metadata', conn=conn, row_id=address)


def delete_erc20s_metadata(conn, addresses):
    toolsql.delete(table='erc20_metadata', conn=conn, row_ids=addresses)

