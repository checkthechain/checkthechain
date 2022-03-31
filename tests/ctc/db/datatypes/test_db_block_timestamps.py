import os
import tempfile

import toolsql

from ctc import db
from ctc.db.datatypes import block_timestamps


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


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


def test_block_timestamps_db():
    db_config = get_test_db_config()
    db_schema = db.get_prepared_schema(
        datatype='block_timestamps',
        network='mainnet',
    )
    toolsql.create_tables(
        db_config=db_config,
        db_schema=db_schema,
    )

    engine = toolsql.create_engine(**db_config)

    # insert data
    with engine.connect() as conn:

        # insert data in bulk
        with conn.begin():
            data = {
                datum['block_number']: datum['timestamp']
                for datum in example_data
            }
            block_timestamps.set_blocks_timestamps(
                conn=conn,
                blocks_timestamps=data,
            )

        # # insert data one-by-one
        # with conn.begin():
        #     for datum in example_data:
        #         block_timestamps.set_block_timestamp(conn=conn, **datum)

        # get data individually
        with conn.begin():
            for datum in example_data:
                timestamp = block_timestamps.get_block_timestamp(
                    conn=conn,
                    block_number=datum['block_number'],
                )
                assert timestamp == datum['timestamp']

        # get data collectively
        all_blocks = [datum['block_number'] for datum in example_data]
        all_timestamps = [datum['timestamp'] for datum in example_data]
        with conn.begin():
            stored_timestamps = block_timestamps.get_blocks_timestamps(
                conn=conn,
                block_numbers=all_blocks,
            )
            assert set(stored_timestamps.values()) == set(all_timestamps)

        # delete entries one by one
        with conn.begin():
            for datum in example_data:
                block_timestamps.delete_block_timestamp(
                    conn=conn,
                    block_number=datum['block_number'],
                )

        # ensure all entries deleted
        with conn.begin():
            stored_timestamps = block_timestamps.get_blocks_timestamps(
                conn=conn,
                block_numbers=all_blocks,
            )
            assert set(stored_timestamps.values()) == {None}

        # insert data again
        with conn.begin():
            for datum in example_data:
                block_timestamps.set_block_timestamp(conn=conn, **datum)

        # delete entries all at once
        with conn.begin():
            block_timestamps.delete_blocks_timestamps(
                conn=conn,
                block_numbers=all_blocks,
            )

        # ensure all entries deleted
        with conn.begin():
            stored_timestamps = block_timestamps.get_blocks_timestamps(
                conn=conn,
                block_numbers=all_blocks,
            )
            assert set(stored_timestamps.values()) == {None}

