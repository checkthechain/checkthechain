import os
import tempfile
import toolsql

from ctc import db
from ctc.db.datatypes import erc20_metadata

example_data = [
    {
        'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        'symbol': 'FEI',
        'decimals': 18,
    },
    {
        'address': '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b',
        'symbol': 'TRIBE',
        'decimals': 18,
    },
    {
        'address': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
        'symbol': 'USDC',
        'decimals': 6,
    },
]


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


def test_create_schema():
    db_config = get_test_db_config()
    db_schema = db.get_prepared_schema(
        datatype='erc20_metadata',
        network='mainnet',
    )
    toolsql.create_tables(
        db_config=db_config,
        db_schema=db_schema,
    )

    engine = toolsql.create_engine(**db_config)

    # insert data
    with engine.connect() as conn:

        # insert data
        with conn.begin():
            for datum in example_data:
                erc20_metadata.insert_erc20_metadata(conn=conn, **datum)

        # get data individually
        with conn.begin():
            for datum in example_data:
                actual_metadata = erc20_metadata.select_erc20_metadata(
                    conn=conn,
                    address=datum['address'],
                )
                for key, target_value in datum.items():
                    assert target_value == actual_metadata[key]

        # get data collectively
        all_addresses = [datum['address'] for datum in example_data]
        with conn.begin():
            actual_metadatas = erc20_metadata.select_erc20s_metadatas(
                conn=conn,
                addresses=all_addresses,
            )
            sorted_example_data = sorted(
                example_data, key=lambda x: x['address']
            )
            sorted_actual_data = sorted(
                actual_metadatas, key=lambda x: x['address']
            )
            for target, actual in zip(sorted_example_data, sorted_actual_data):
                assert target == actual

        # delete entries one by one
        with conn.begin():
            for datum in example_data:
                erc20_metadata.delete_erc20_metadata(
                    conn=conn,
                    address=datum['address'],
                )

        # ensure all entries deleted
        with conn.begin():
            actual_metadatas = erc20_metadata.select_erc20s_metadatas(
                conn=conn,
                addresses=all_addresses,
            )
            assert all(item is None for item in actual_metadatas)

        # insert data again
        with conn.begin():
            for datum in example_data:
                erc20_metadata.insert_erc20_metadata(conn=conn, **datum)

        # delete entries all at once
        with conn.begin():
            erc20_metadata.delete_erc20s_metadata(
                conn=conn,
                addresses=all_addresses,
            )

        # ensure all entries deleted
        with conn.begin():
            actual_metadatas = erc20_metadata.select_erc20s_metadatas(
                conn=conn,
                addresses=all_addresses,
            )
            assert all(item is None for item in actual_metadatas)

