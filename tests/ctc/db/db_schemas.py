import pytest

from ctc import db


# test that every schema exists and is retrievable
@pytest.mark.parametrize('schema_name', db.get_schema_names())
def test_db_names_have_db_schemas(schema_name):
    db.get_raw_schema(schema_name)


@pytest.mark.parameterize('schema_name', db.get_schema_names())
def test_every_evm_schema_active_status_listed(schema_name):
    active_schemas = db.get_active_schemas()
    assert schema_name in active_schemas
