import toolsql

from ctc import db

import conftest


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


async def test_create_creation_blocks_crud():
    db_config = conftest.get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='contract_creation_blocks',
        context=dict(network='ethereum'),
    )
    toolsql.create_db(
        db_config=db_config,
        db_schema=db_schema,
        if_not_exists=True,
        confirm=True,
    )

    # insert data
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_upsert_contract_creation_block(
                conn=conn, **datum
            )

    # get data individually
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            stored_block = await db.async_select_contract_creation_block(
                conn=conn,
                address=datum['address'],
            )
            assert stored_block == datum['block_number']

    # delete entries one by one
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_delete_contract_creation_block(
                conn=conn,
                address=datum['address'],
            )

    # ensure all entries deleted
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            block = await db.async_select_contract_creation_block(
                conn=conn,
                address=datum['address'],
            )
            assert block is None

