import pytest

from ctc import spec
from ctc.spec import typedefs
from ctc.config import config_defaults
from ctc.config import config_validate


default_db_configs = config_defaults.get_default_db_configs('/path/to/data')

valid_values = {
    'config_spec_version': ['0.3.0'],
    'data_dir': ['/path/to/data'],
    'networks': [
        {
            1: {
                'name': 'mainnet',
                'chain_id': 1,
                'block_explorer': 'etherscan.io',
            },
        },
        {
            1: {
                'name': 'mainnet',
                'chain_id': 1,
                'block_explorer': None,
            },
        },
        {},
    ],
    'providers': [
        {
            'test_provider': {
                'name': 'test_provider',
                'url': 'http://some_url.com',
                'network': 1,
                'protocol': 'http',
                'session_kwargs': {},
                'chunk_size': None,
                'convert_reverts_to_none': False,
            },
        },
        {
            'test_provider': {
                'name': 'test_provider',
                'url': 'https://some_url.com',
                'network': 1,
                'protocol': 'http',
                'session_kwargs': {},
                'chunk_size': None,
                'convert_reverts_to_none': False,
            },
        },
    ],
    'default_network': [1],
    'default_providers': [{}],
    'db_configs': [default_db_configs],
    'log_rpc_calls': [True, False],
    'log_sql_queries': [True, False],
}

invalid_values = {
    'config_spec_version': ['0.3.0b', '0.2.10', None],
    'data_dir': ['relpath/to/data'],
    'networks': [
        {
            'mainnet': {
                'name': 'mainnet',
                'chain_id': 1,
                'block_explorer': 'etherscan.io',
            },
        },
        {
            1: {
                'name': 'mainnet',
                'chain_id': 'mainnet',
                'block_explorer': 'etherscan.io',
            },
        },
    ],
    'providers': [
        {'hi': {}},
        {
            'test_provider': {
                'name': 'test_provider',
                'url': 'some_url.com',
                'network': 1,
                'protocol': 'http',
                'session_kwargs': {},
                'chunk_size': None,
                'convert_reverts_to_none': False,
            },
        },
        {
            'test_provider': {
                'name': 'test_provider_different_name',
                'url': 'some_url.com',
                'network': 1,
                'protocol': 'http',
                'session_kwargs': {},
                'chunk_size': None,
                'convert_reverts_to_none': False,
            },
        },
    ],
    'default_network': [888, 'mainnet'],
    'default_providers': [{888: None}, {'mainnet': None}],
    'db_configs': [
        {},
        dict(default_db_configs, main2=default_db_configs['main']),
    ],
    'log_rpc_calls': [None, 'a', 2],
    'log_sql_queries': [None, 'a', 2],
}


def test_every_config_key_has_validator_entry():
    config_spec = list(typedefs.Config.__annotations__.keys())
    config_validators = config_validate.get_config_validators()
    for key in config_spec:
        assert key in config_validators
    for key in config_validators:
        assert key in config_spec


@pytest.mark.parametrize('item', list(valid_values.items()))
def test_validate_valid_config_values(item):

    key, values = item

    base_type = config_validate.get_config_base_types()[key]
    validator = config_validate.get_config_validators()[key]
    default_config = config_defaults.get_default_config()

    for value in values:
        assert isinstance(value, base_type)
        if validator is not None:
            validator(value, default_config)


@pytest.mark.parametrize('item', list(invalid_values.items()))
def test_validate_invalid_config_values(item):
    key, values = item

    base_type = config_validate.get_config_base_types()[key]
    validator = config_validate.get_config_validators()[key]
    default_config = config_defaults.get_default_config()

    for value in values:
        if not isinstance(value, base_type):
            continue
        if validator is not None:
            with pytest.raises(spec.ConfigInvalid):
                validator(value, default_config)
