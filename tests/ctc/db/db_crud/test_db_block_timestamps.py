import toolsql

from ctc import db

import conftest


example_data = [
    {
        'block_number': 14000000,
        'timestamp': 1642114795,
    },
    {
        'block_number': 14000001,
        'timestamp': 1642114800,
    },
    {
        'block_number': 14000002,
        'timestamp': 1642114824,
    },
    {
        'block_number': 14000003,
        'timestamp': 1642114825,
    },
    {
        'block_number': 14000004,
        'timestamp': 1642114850,
    },
    {
        'block_number': 14000005,
        'timestamp': 1642114852,
    },
    {
        'block_number': 14000006,
        'timestamp': 1642114865,
    },
    {
        'block_number': 14000007,
        'timestamp': 1642114881,
    },
    {
        'block_number': 14000008,
        'timestamp': 1642114895,
    },
    {
        'block_number': 14000009,
        'timestamp': 1642114917,
    },
]


async def test_block_timestamps_db():
    db_config = conftest.get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='block_timestamps',
        context=dict(network='ethereum'),
    )
    toolsql.create_db(
        db_config=db_config,
        db_schema=db_schema,
        if_not_exists=True,
        confirm=True,
    )

    # insert data one-by-one
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_upsert_block_timestamp(conn=conn, **datum)

    # get data individually
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            timestamp = await db.async_select_block_timestamp(
                conn=conn,
                block_number=datum['block_number'],
            )
            assert timestamp == datum['timestamp']

    # get data collectively
    all_blocks = [datum['block_number'] for datum in example_data]
    all_timestamps = [datum['timestamp'] for datum in example_data]
    async with toolsql.async_connect(db_config) as conn:
        stored_timestamps = await db.async_select_block_timestamps(
            conn=conn,
            block_numbers=all_blocks,
        )
        assert set(stored_timestamps) == set(all_timestamps)

    # delete entries one by one
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_delete_block_timestamp(
                conn=conn,
                block_number=datum['block_number'],
            )

    # ensure all entries deleted
    async with toolsql.async_connect(db_config) as conn:
        stored_timestamps = await db.async_select_block_timestamps(
            conn=conn,
            block_numbers=all_blocks,
        )
        assert set(stored_timestamps) == {None}

    # insert data again
    async with toolsql.async_connect(db_config) as conn:
        for datum in example_data:
            await db.async_upsert_block_timestamp(conn=conn, **datum)

    # delete entries all at once
    async with toolsql.async_connect(db_config) as conn:
        await db.async_delete_block_timestamps(
            conn=conn,
            block_numbers=all_blocks,
        )

    # ensure all entries deleted
    async with toolsql.async_connect(db_config) as conn:
        stored_timestamps = await db.async_select_block_timestamps(
            conn=conn,
            block_numbers=all_blocks,
        )
        assert set(stored_timestamps) == {None}
