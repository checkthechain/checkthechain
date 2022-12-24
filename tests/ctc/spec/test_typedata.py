from ctc import spec
from ctc.spec.typedefs import block_types
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

