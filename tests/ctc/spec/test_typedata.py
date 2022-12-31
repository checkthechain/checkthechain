from ctc import spec
from ctc.spec.typedefs import block_types
from ctc.spec.typedefs import db_types
from ctc.spec.typedefs import config_types


def test_config_keys_match_types():
    assert set(spec.config_keys) == set(
        config_types.Config.__annotations__.keys()
    )
    assert set(spec.config_keys) == set(
        config_types.PartialConfig.__annotations__.keys()
    )
    assert set(spec.config_keys) == set(
        config_types.JsonConfig.__annotations__.keys()
    )


def test_block_keys_match_types():
    assert set(spec.block_keys) == set(block_types.Block.__annotations__.keys())


def test_schema_names_match_schema_types():
    assert set(spec.schema_names) == (
        set(db_types.AdminSchemaName.__args__)
        .union(set(db_types.GenericSchemaName.__args__))
        .union(set(db_types.NetworkSchemaName.__args__))
    )


def test_network_schema_names_match_schema_types():
    assert set(spec.network_schema_names) == set(db_types.NetworkSchemaName.__args__)

