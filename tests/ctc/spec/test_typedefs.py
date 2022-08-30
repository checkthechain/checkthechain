from ctc.spec import typedefs


def test_config_specs_match():
    assert set(typedefs.Config.__annotations__.keys()) == set(
        typedefs.PartialConfig.__annotations__.keys()
    )
    assert set(typedefs.Config.__annotations__.keys()) == set(
        typedefs.JsonConfig.__annotations__.keys()
    )

    for key, value in typedefs.Config.__annotations__.items():
        assert value == typedefs.PartialConfig.__annotations__[key]
        if key not in ['networks', 'default_providers']:
            assert value == typedefs.JsonConfig.__annotations__[key]
