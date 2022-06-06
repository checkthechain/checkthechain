
from ctc import config


def test_config_overrides():

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
