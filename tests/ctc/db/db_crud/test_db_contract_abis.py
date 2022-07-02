import os
import tempfile
import toolsql

from ctc import db


example_data = [
    {
        'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        'abi': {'fake': 'abi', 'nested': {'attribute': 'value'}},
        'includes_proxy': False,
    },
    {
        'address': '0x9928e4046d7c6513326ccea028cd3e7a91c7590a',
        'abi': {
            'another_fake': 'abi',
            'another_nested': {'attribute': 'value'},
        },
        'includes_proxy': False,
    },
]


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


async def test_contract_abis_crud():

    db_config = get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='contract_abis',
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
                await db.async_upsert_contract_abi(conn=conn, **datum)

        # get data individually
        with conn.begin():
            for datum in example_data:
                db_contract_abi = await db.async_select_contract_abi(
                    conn=conn,
                    address=datum['address'],
                )
                assert datum['abi'] == db_contract_abi
                # for key, target_value in datum.items():
                #     assert target_value == db_contract_abi[key]

        # get data collectively
        all_addresses = [datum['address'] for datum in example_data]
        with conn.begin():
            db_contract_abis = await db.async_select_contract_abis(
                conn=conn,
                addresses=all_addresses,
            )
            packaged_example_data = {
                datum['address']: datum['abi'] for datum in example_data
            }
            assert db_contract_abis == packaged_example_data

        # delete entries one by one
        with conn.begin():
            for datum in example_data:
                await db.async_delete_contract_abi(
                    conn=conn,
                    address=datum['address'],
                )

        # ensure all entries deleted
        with conn.begin():
            db_contract_abis = await db.async_select_contract_abis(
                conn=conn,
                addresses=all_addresses,
            )
            assert all(item is None for item in db_contract_abis)

        # insert data again
        with conn.begin():
            for datum in example_data:
                await db.async_upsert_contract_abi(conn=conn, **datum)
