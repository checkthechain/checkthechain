import pytest

from ctc import config


@pytest.fixture
def override_clearer():
    yield
    config.clear_config_overrides()


def test_config_overrides(override_clearer):

    # get old config
    old_config = config.get_config()

    # set override
    key = 'data_dir'
    value = '/some/new/dir'
    assert old_config[key] != value
    config.set_config_override(key=key, value=value)

    # conform that override tracked
    overrides = config.get_config_overrides()
    assert len(overrides) == 1

    # confirm override in config
    new_config = config.get_config()
    assert value == new_config[key]

    # clear override
    config.clear_config_override(key)
    newest_config = config.get_config()
    assert old_config[key] == newest_config[key]
