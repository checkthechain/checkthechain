from ctc import spec


def test_config_specs_match():
    assert set(spec.Config.__annotations__.keys()) == set(
        spec.PartialConfig.__annotations__.keys()
    )

    for key, value in spec.Config.__annotations__.items():
        assert value == spec.PartialConfig.__annotations__[key]

