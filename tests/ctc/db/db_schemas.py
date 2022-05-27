import pytest

from ctc import db


# test that every schema exists and is retrievable
@pytest.mark.parametrize('schema_name', db.get_schema_names())
def test_db_names_have_db_schemas(schema_name):
    db.get_raw_schema(schema_name)
