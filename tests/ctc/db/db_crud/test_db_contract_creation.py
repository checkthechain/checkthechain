import os
import tempfile
import toolsql

from ctc import db


example_data = [
    {
        'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        'block_number': 12125705,
    },
    {
        'address': '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b',
        'block_number': 12125705,
    },
    {
        'address': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
        'block_number': 6082465,
    },
]


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


async def test_create_creation_blocks_crud():
    db_config = get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='contract_creation_blocks',
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
                await db.async_upsert_contract_creation_block(
                    conn=conn, **datum
                )

        # get data individually
        with conn.begin():
            for datum in example_data:
                stored_block = await db.async_select_contract_creation_block(
                    conn=conn,
                    address=datum['address'],
                )
                assert stored_block == datum['block_number']

        # delete entries one by one
        with conn.begin():
            for datum in example_data:
                await db.async_delete_contract_creation_block(
                    conn=conn,
                    address=datum['address'],
                )

        # ensure all entries deleted
        with conn.begin():
            for datum in example_data:
                block = await db.async_select_contract_creation_block(
                    conn=conn,
                    address=datum['address'],
                )
                assert block is None
