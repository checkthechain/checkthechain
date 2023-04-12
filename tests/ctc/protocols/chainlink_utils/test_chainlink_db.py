
import toolsql

from ctc import db
from ctc.protocols.chainlink_utils import chainlink_db

import conftest


async def test_get_chainlink_feed_payload():
    await chainlink_db.async_get_complete_feed_payload()


async def test_populate_feeds():
    db_config = conftest.get_test_db_config()
    with toolsql.connect(db_config) as conn:
        db.initialize_schema(
            schema_name='chainlink',
            context=dict(network='ethereum'),
            conn=conn,
        )
    async with toolsql.async_connect(db_config) as conn:
        await chainlink_db.async_import_network_to_db(
            network='ethereum',
            conn=conn,
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

    db_config = conftest.get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='chainlink',
        context=dict(network='ethereum'),
    )
    toolsql.create_db(
        db_config=db_config,
        db_schema=db_schema,
        if_not_exists=True,
        confirm=True,
    )

    network = 1

    # insert data
    async with toolsql.async_connect(db_config) as conn:
        for feed_data in example_data:
            await chainlink_db.async_upsert_feed(
                conn=conn,
                feed=feed_data,
                context=dict(network=network),
            )

    # get data individually
    async with toolsql.async_connect(db_config) as conn:
        for feed_data in example_data:
            db_feed = await chainlink_db.async_select_feed(
                conn=conn,
                address=feed_data['address'],
                context=dict(network=network),
            )
            for key, target_value in feed_data.items():
                assert target_value == db_feed[key]

    # get data collectively
    async with toolsql.async_connect(db_config) as conn:
        addresses = [feed_data['address'] for feed_data in example_data]
        db_feeds = await chainlink_db.async_select_feeds(
            conn=conn,
            addresses=addresses,
            context=dict(network=network),
        )
        db_feeds = sorted(db_feeds, key=lambda feed: feed['address'])
        assert db_feeds == example_data

    # delete entries one by one
    async with toolsql.async_connect(db_config) as conn:
        for feed_data in example_data:
            await chainlink_db.async_delete_feed(
                conn=conn,
                address=feed_data['address'],
                context=dict(network=network),
            )

    # ensure all entries deleted
    async with toolsql.async_connect(db_config) as conn:
        db_feeds = await chainlink_db.async_select_feeds(
            conn=conn,
            addresses=addresses,
            context=dict(network=network),
        )
        assert all(item is None for item in db_feeds)

