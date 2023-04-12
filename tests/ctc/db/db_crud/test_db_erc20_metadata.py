import toolsql

from ctc import db

import conftest


example_data = [
    {
        'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        'symbol': 'FEI',
        'decimals': 18,
        'name': 'Fei USD',
    },
    {
        'address': '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b',
        'symbol': 'TRIBE',
        'decimals': 18,
        'name': 'Tribe',
    },
]


async def test_erc20_metadata_crud():
    db_config = conftest.get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='erc20_metadata',
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
        await db.async_upsert_erc20s_metadata(
            conn=conn,
            erc20s_metadata=example_data,
            context=dict(network=1),
        )

    # get data individually
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            actual_metadata = await db.async_select_erc20_metadata(
                conn=conn,
                address=datum['address'],
            )
            for key, target_value in datum.items():
                assert target_value == actual_metadata[key]

    # get data collectively
    all_addresses = [datum['address'] for datum in example_data]
    async with toolsql.async_connect(db_config) as conn:
        actual_metadatas = await db.async_select_erc20s_metadata(
            conn=conn,
            addresses=all_addresses,
        )
        sorted_example_data = sorted(example_data, key=lambda x: x['address'])
        sorted_actual_data = sorted(
            actual_metadatas, key=lambda x: x['address']
        )
        for target, actual in zip(sorted_example_data, sorted_actual_data):
            assert target == actual

    # delete entries one by one
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_delete_erc20_metadata(
                conn=conn,
                address=datum['address'],
                context=dict(network=1),
            )

    # ensure all entries deleted
    async with toolsql.async_connect(db_config) as conn:
        actual_metadatas = await db.async_select_erc20s_metadata(
            conn=conn,
            addresses=all_addresses,
        )
        assert all(item is None for item in actual_metadatas)

    # insert data again
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_upsert_erc20_metadata(
                conn=conn, context=dict(network=1), **datum
            )

    # delete entries all at once
    async with toolsql.async_connect(db_config) as conn:
        await db.async_delete_erc20s_metadata(
            conn=conn,
            addresses=all_addresses,
            context=dict(network=1),
        )

    # ensure all entries deleted
    async with toolsql.async_connect(db_config) as conn:
        actual_metadatas = await db.async_select_erc20s_metadata(
            conn=conn,
            addresses=all_addresses,
        )
        assert all(item is None for item in actual_metadatas)

