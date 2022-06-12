import os
import tempfile

import toolsql

from ctc import db
from ctc.protocols import chainlink_utils


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


async def test_get_chainlink_feed_payload():
    await chainlink_utils.async_get_complete_feed_payload()


async def test_populate_feeds():
    db_config = get_test_db_config()
    engine = toolsql.create_engine(db_config=db_config)
    with engine.begin() as conn:
        db.initialize_schema(schema_name='chainlink', network='mainnet', conn=conn)
    await chainlink_utils.async_import_network_to_db(network='mainnet', engine=engine)
