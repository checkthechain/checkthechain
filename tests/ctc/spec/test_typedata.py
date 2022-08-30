
from ctc import spec
from ctc.spec import typedefs


def test_config_keys_match_types():
    assert set(spec.config_keys) == set(typedefs.Config.__annotations__.keys())
    assert set(spec.config_keys) == set(typedefs.PartialConfig.__annotations__.keys())
    assert set(spec.config_keys) == set(typedefs.JsonConfig.__annotations__.keys())


def test_block_keys_match_types():
    assert set(spec.block_keys) == set(typedefs.Block.__annotations__.keys())
