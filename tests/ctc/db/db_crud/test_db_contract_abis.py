import os
import tempfile
import toolsql

from ctc import db


example_data = {
}


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
                for key, target_value in datum.items():
                    assert target_value == db_contract_abi[key]

        # get data collectively
        all_addresses = [datum['address'] for datum in example_data]
        with conn.begin():
            db_contract_abis = await db.async_select_contract_abis(
                conn=conn,
                addresses=all_addresses,
            )
            sorted_example_data = sorted(
                example_data, key=lambda x: x['address']
            )
            sorted_db_data = sorted(
                db_contract_abis, key=lambda x: x['address']
            )
            for target_db, db_data in zip(sorted_example_data, sorted_db_data):
                assert target_db == db_data

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
