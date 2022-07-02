import os
import tempfile
import toolsql

from ctc import db


example_data = [
    {
        'number': 100,
        'difficulty': 17916437174,
        'extra_data': '0x476574682f4c5649562f76312e302e302f6c696e75782f676f312e342e32',
        'gas_limit': 5000,
        'gas_used': 0,
        'hash': '0xdfe2e70d6c116a541101cecbb256d7402d62125f6ddc9b607d49edc989825c64',
        'logs_bloom': '0x0',
        'miner': '0xbb7b8287f3f0a933474a79eae42cbca977791171',
        'mix_hash': '0x5bb43c0772e58084b221c8e0c859a45950c103c712c5b8f11d9566ee078a4501',
        'nonce': '0x37129c7f29a9364b',
        'parent_hash': '0xdb10afd3efa45327eb284c83cc925bd9bd7966aea53067c1eebe0724d124ec1e',
        'receipts_root': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
        'sha3_uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
        'size': 542,
        'state_root': '0x90c25f6d7fddeb31a6cc5668a6bba77adbadec705eb7aa5a51265c2d1e3bb7ac',
        'timestamp': 1438270443,
        'total_difficulty': '1766758139014',
        'transactions': [],
        'transactions_root': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
        'uncles': [],
    },
    {
        'number': 101,
        'difficulty': 17925185434,
        'extra_data': '0x476574682f4c5649562f76312e302e302f6c696e75782f676f312e342e32',
        'gas_limit': 5000,
        'gas_used': 0,
        'hash': '0x4f66fd0241681ebbc119f97e952c1036b87b6e8f64f5c5d84c5c7a9bb1ebfdcc',
        'logs_bloom': '0x0',
        'miner': '0xbb7b8287f3f0a933474a79eae42cbca977791171',
        'mix_hash': '0xf086f1bc68d5a15cd06ac2017e82e8a02399d6667896a224b65a32600425a08d',
        'nonce': '0x4587d7ffc0496ea5',
        'parent_hash': '0xdfe2e70d6c116a541101cecbb256d7402d62125f6ddc9b607d49edc989825c64',
        'receipts_root': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
        'sha3_uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
        'size': 542,
        'state_root': '0xc66500dc36b0af946808ab610894d1b8af50a6033e4d92ba93236edc66649c01',
        'timestamp': 1438270445,
        'total_difficulty': '1784683324448',
        'transactions': [],
        'transactions_root': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
        'uncles': [],
    },
    {
        'number': 102,
        'difficulty': 17933937965,
        'extra_data': '0x476574682f76312e302e302f6c696e75782f676f312e342e32',
        'gas_limit': 5000,
        'gas_used': 0,
        'hash': '0x16110f3aa1895de2ec22cfd746751f724d112a953c71b62858a1523b50f3dc64',
        'logs_bloom': '0x0',
        'miner': '0x28921e4e2c9d84f4c0f0c0ceb991f45751a0fe93',
        'mix_hash': '0xf3277624282cb1e4f3db0e97fb2be539674fc1d6b9c3cc91014ececa73083ba8',
        'nonce': '0x8d36eecca27a8e00',
        'parent_hash': '0x4f66fd0241681ebbc119f97e952c1036b87b6e8f64f5c5d84c5c7a9bb1ebfdcc',
        'receipts_root': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
        'sha3_uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
        'size': 537,
        'state_root': '0x02607447cef691e3d873cf5a1d88ac201813353147ee0d631789ec757accfa6b',
        'timestamp': 1438270447,
        'total_difficulty': '1802617262413',
        'transactions': [],
        'transactions_root': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
        'uncles': [],
    },
]


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


async def test_blocks_crud():

    db_config = get_test_db_config()
    db_schema = db.get_prepared_schema(
        schema_name='blocks',
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
            for block in example_data:
                await db.async_upsert_block(
                    conn=conn, block=block, network=network
                )

        # get data individually
        with conn.begin():
            for block in example_data:
                db_block = await db.async_select_block(
                    conn=conn,
                    block_number=block['number'],
                    network=network,
                )
                for key, target_value in block.items():
                    assert target_value == db_block[key]

        # get data collectively
        with conn.begin():
            block_numbers = [block['number'] for block in example_data]
            db_blocks = await db.async_select_blocks(
                conn=conn,
                block_numbers=block_numbers,
                network=network,
            )
            db_blocks = sorted(db_blocks, key=lambda block: block['number'])
            assert db_blocks == example_data

        # delete entries one by one
        with conn.begin():
            for block in example_data:
                await db.async_delete_block(
                    conn=conn,
                    block_number=block['number'],
                    network=network,
                )

        # ensure all entries deleted
        with conn.begin():
            db_blocks = await db.async_select_blocks(
                conn=conn,
                block_numbers=block_numbers,
                network=network,
            )
            assert all(item is None for item in db_blocks)
