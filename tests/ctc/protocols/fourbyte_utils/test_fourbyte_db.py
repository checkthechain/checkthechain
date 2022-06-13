import os
import tempfile

import toolsql

from ctc import db
from ctc.protocols import fourbyte_utils


example_data = [
    {
        'id': 145,
        'created_at': '2016-07-09T03:58:28.234977Z',
        'text_signature': 'transfer(address,uint256)',
        'hex_signature': '0xa9059cbb',
        'bytes_signature': '©\x05\x9c»',
    },
    {
        'id': 179,
        'created_at': '2016-07-09T03:58:45.230129Z',
        'hex_signature': '0x18160ddd',
        'text_signature': 'totalSupply()',
        'bytes_signature': '\x18\x16\rÝ',
    },
    {
        'id': 31780,
        'created_at': '2018-05-11T08:39:29.708250Z',
        'text_signature': 'many_msg_babbage(bytes1)',
        'hex_signature': '0xa9059cbb',
        'bytes_signature': '©\x05\x9c»',
    },
    {
        'id': 161159,
        'created_at': '2019-03-22T19:13:17.314877Z',
        'text_signature': 'transfer(bytes4[9],bytes5[6],int48[11])',
        'hex_signature': '0xa9059cbb',
        'bytes_signature': '©\x05\x9c»',
    },
    {
        'id': 313067,
        'created_at': '2021-10-20T05:29:13.555535Z',
        'text_signature': 'func_2093253501(bytes)',
        'hex_signature': '0xa9059cbb',
        'bytes_signature': '©\x05\x9c»',
    },
]


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


async def test_fourbyte_crud():

    db_config = get_test_db_config()
    db_schema = db.get_raw_schema(schema_name='4byte')
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
                await fourbyte_utils.async_upsert_function_signature(
                    conn=conn,
                    function_signature=datum,
                )

        # get data individually
        with conn.begin():
            for datum in example_data:
                db_data = await fourbyte_utils.async_select_function_signatures(
                    conn=conn,
                    id=datum['id'],
                )
                db_datum = db_data[0]
                for key, target_value in datum.items():
                    assert target_value == db_datum[key]

        # get data collectively
        with conn.begin():
            for datum in example_data:
                db_datas = (
                    await fourbyte_utils.async_select_function_signatures(
                        conn=conn,
                        hex_signature=datum['hex_signature'],
                    )
                )
                assert len(db_datas) > 0

        # delete entries one by one
        with conn.begin():
            for datum in example_data:
                await fourbyte_utils.async_delete_function_signatures(
                    conn=conn,
                    text_signature=datum['text_signature'],
                )

        # ensure all entries deleted
        with conn.begin():
            db_datas = await fourbyte_utils.async_select_function_signatures(
                conn=conn,
            )
            assert len(db_datas) == 0
