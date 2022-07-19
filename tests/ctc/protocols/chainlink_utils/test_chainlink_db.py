import os
import tempfile

import toolsql

from ctc import db
from ctc.protocols.chainlink_utils import chainlink_db


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


async def test_get_chainlink_feed_payload():
    await chainlink_db.async_get_complete_feed_payload()


async def test_populate_feeds():
    db_config = get_test_db_config()
    engine = toolsql.create_engine(db_config=db_config)
    with engine.begin() as conn:
        db.initialize_schema(
            schema_name='chainlink', network='mainnet', conn=conn
        )
    await chainlink_db.async_import_network_to_db(
        network='mainnet', engine=engine
    )


example_data = [
    {
        'address': '0x31e0a88fecb6ec0a411dbe0e9e76391498296ee9',
        'name': 'FEI / USD',
        'deviation': '1',
        'heartbeat': '1h',
        'decimals': 8,
        'asset': 'FEI Protocol',
        'asset_type': 'Crypto',
        'status': 'verified',
    },
    {
        'address': '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419',
        'name': 'ETH / USD',
        'deviation': '0.5',
        'heartbeat': '1h',
        'decimals': 8,
        'asset': 'Ethereum',
        'asset_type': 'Crypto',
        'status': 'verified',
    },
]


async def test_chainlink_crud():

    db_config = get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='chainlink',
        network='mainnet',
    )
    toolsql.create_tables(
        db_config=db_config,
        db_schema=db_schema,
    )

    engine = toolsql.create_engine(**db_config)

    network = 1

    # insert data
    with engine.connect() as conn:

        # insert data
        with conn.begin():
            for feed_data in example_data:
                await chainlink_db.async_upsert_feed(
                    conn=conn, feed=feed_data, network=network
                )

        # get data individually
        with conn.begin():
            for feed_data in example_data:
                db_feed = await chainlink_db.async_select_feed(
                    conn=conn,
                    address=feed_data['address'],
                    network=network,
                )
                for key, target_value in feed_data.items():
                    assert target_value == db_feed[key]

        # get data collectively
        with conn.begin():
            addresses = [feed_data['address'] for feed_data in example_data]
            db_feeds = await chainlink_db.async_select_feeds(
                conn=conn,
                addresses=addresses,
                network=network,
            )
            db_feeds = sorted(db_feeds, key=lambda feed: feed['address'])
            assert db_feeds == example_data

        # delete entries one by one
        with conn.begin():
            for feed_data in example_data:
                await chainlink_db.async_delete_feed(
                    conn=conn,
                    address=feed_data['address'],
                    network=network,
                )

        # ensure all entries deleted
        with conn.begin():
            db_feeds = await chainlink_db.async_select_feeds(
                conn=conn,
                addresses=addresses,
                network=network,
            )
            assert all(item is None for item in db_feeds)
