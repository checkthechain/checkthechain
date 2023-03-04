
import toolsql
import pytest

import ctc
from ctc import db

import conftest


def test_initialize_schema_version_schema():
    db_config = conftest.get_test_db_config()
    with toolsql.connect(db_config) as conn:
        db.initialize_schema_versions(conn=conn)
    with toolsql.connect(db_config) as conn:
        assert db.is_schema_versions_initialized(conn=conn)


@pytest.mark.parametrize(
    'schema_name', db.get_evm_schema_names() + db.get_generic_schema_names()
)
def test_initialize_schemas(schema_name):

    db_config = conftest.get_test_db_config()
    network = 1

    # create schema
    with toolsql.connect(db_config) as conn:
        db.initialize_schema(
            schema_name=schema_name,
            network=network,
            conn=conn,
        )

    # assert that schema version being tracked
    with toolsql.connect(db_config) as conn:
        schema_version = db.get_schema_version(
            schema_name=schema_name,
            context=dict(network=network),
            conn=conn,
        )
        assert schema_version == ctc.__version__

