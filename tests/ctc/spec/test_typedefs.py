from ctc import spec


def test_config_specs_match():
    assert set(spec.Config.__annotations__.keys()) == set(
        spec.PartialConfig.__annotations__.keys()
    )
    assert set(spec.Config.__annotations__.keys()) == set(
        spec.JsonConfig.__annotations__.keys()
    )

    for key, value in spec.Config.__annotations__.items():
        assert value == spec.PartialConfig.__annotations__[key]
        if key not in ['networks', 'default_providers']:
            assert value == spec.JsonConfig.__annotations__[key]
