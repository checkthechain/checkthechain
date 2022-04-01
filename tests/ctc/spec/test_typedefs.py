from ctc import spec


def test_config_specs_match():
    assert set(spec.ConfigSpec.__annotations__.keys()) == set(
        spec.PartialConfigSpec.__annotations__.keys()
    )

