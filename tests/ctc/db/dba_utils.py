import os
import tempfile

import toolsql
import pytest

import ctc
from ctc import db


def get_test_db_config():
    tempdir = tempfile.mkdtemp()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(tempdir, 'example.db'),
    }


def test_initialize_schema_version_schema():
    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)
    with engine.begin() as conn:
        db.initialize_schema_versions(conn=conn)
    assert db.is_schema_versions_initialized(engine=engine)


@pytest.mark.parametrize(
    'schema_name', db.get_evm_schema_names() + db.get_generic_schema_names()
)
def test_initialize_schemas(schema_name):

    db_config = get_test_db_config()
    engine = toolsql.create_engine(**db_config)
    network = 1

    # create schema
    with engine.begin() as conn:
        db.initialize_schema(
            schema_name=schema_name,
            network=network,
            conn=conn,
        )

    # assert that schema version being tracked
    with engine.begin() as conn:
        schema_version = db.get_schema_version(
            schema_name=schema_name,
            network=network,
            conn=conn,
        )
        assert schema_version == ctc.__version__
