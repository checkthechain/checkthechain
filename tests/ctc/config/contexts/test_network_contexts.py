import pytest

import ctc.config

example_context_config = {
    'default_network': 42161,
    'default_providers': {
        1: 'alchemy__1',
        42161: 'alchemy__42161',
    },
    'providers': {
        'infura__1': {
            'chunk_size': None,
            'convert_reverts_to_none': False,
            'name': 'infura__1',
            'network': 1,
            'protocol': 'http',
            'session_kwargs': {},
            'url': 'http://1.infura.com',
            'disable_batch_requests': False,
        },
        'infura__42161': {
            'chunk_size': None,
            'convert_reverts_to_none': False,
            'name': 'infura__42161',
            'network': 42161,
            'protocol': 'http',
            'session_kwargs': {},
            'url': 'http://42161.infura.com',
            'disable_batch_requests': False,
        },
        'alchemy__1': {
            'chunk_size': None,
            'convert_reverts_to_none': False,
            'name': 'alchemy__1',
            'network': 1,
            'protocol': 'http',
            'session_kwargs': {},
            'url': 'http://1.alchemy.com',
            'disable_batch_requests': False,
        },
        'alchemy__42161': {
            'chunk_size': None,
            'convert_reverts_to_none': False,
            'name': 'alchemy__42161',
            'network': 42161,
            'protocol': 'http',
            'session_kwargs': {},
            'url': 'http://42161.alchemy.com',
            'disable_batch_requests': False,
        },
    },
}

default_network = example_context_config['default_network']
default_provider = example_context_config['providers'][
    example_context_config['default_providers'][default_network]
]

example_context_tests = [
    #
    # defaults
    {
        'context': {},
        'chain_id': default_network,
        'provider_url': default_provider['url'],
    },
    {
        'context': {'provider': None},
        'chain_id': default_network,
        'provider_url': default_provider['url'],
    },
    {
        'context': {
            'provider': None,
        },
        'chain_id': default_network,
        'provider_url': default_provider['url'],
    },
    {
        'context': {'network': None},
        'chain_id': default_network,
        'provider_url': default_provider['url'],
    },
    #
    # provider by name
    {
        'context': {'provider': 'infura__1'},
        'chain_id': 1,
        'provider_url': 'http://1.infura.com',
    },
    {
        'context': {'provider': 'infura__42161'},
        'chain_id': 42161,
        'provider_url': 'http://42161.infura.com',
    },
    {
        'context': {'provider': 'alchemy__1'},
        'chain_id': 1,
        'provider_url': 'http://1.alchemy.com',
    },
    {
        'context': {'provider': 'alchemy__42161'},
        'chain_id': 42161,
        'provider_url': 'http://42161.alchemy.com',
    },
    #
    # provider by known url
    {
        'context': {'provider': 'http://1.infura.com'},
        'chain_id': 1,
        'provider_url': 'http://1.infura.com',
    },
    {
        'context': {'provider': 'http://42161.infura.com'},
        'chain_id': 42161,
        'provider_url': 'http://42161.infura.com',
    },
    {
        'context': {'provider': 'http://1.alchemy.com'},
        'chain_id': 1,
        'provider_url': 'http://1.alchemy.com',
    },
    {
        'context': {'provider': 'http://42161.alchemy.com'},
        'chain_id': 42161,
        'provider_url': 'http://42161.alchemy.com',
    },
    #
    # provider by unknown url
    {
        'context': {'provider': 'https://arbitrumrpc.com'},
        'chain_id': 42161,
        'provider_url': 'https://arbitrumrpc.com',
    },
    #
    # provider by chain id
    {
        'context': {'network': 1},
        'chain_id': 1,
        'provider_url': 'http://1.alchemy.com',
    },
    {
        'context': {'network': 42161},
        'chain_id': 42161,
        'provider_url': 'http://42161.alchemy.com',
    },
    #
    # provider by network name
    {
        'context': {'network': 'ethereum'},
        'chain_id': 1,
        'provider_url': 'http://1.alchemy.com',
    },
    {
        'context': {'network': 'arbitrum'},
        'chain_id': 42161,
        'provider_url': 'http://42161.alchemy.com',
    },
]


@pytest.fixture()
def set_example_context_config():
    import ctc.config

    for key, value in example_context_config.items():
        ctc.config.set_config_override(key=key, value=value)

    yield

    ctc.config.clear_all_config_overrides()


@pytest.mark.parametrize('test', example_context_tests)
def test_get_context_chain_id(test, set_example_context_config):
    context = test['context']
    target_chain_id = test['chain_id']
    actual_chain_id = ctc.config.get_context_chain_id(context)
    assert actual_chain_id == target_chain_id


@pytest.mark.parametrize('test', example_context_tests)
def test_get_context_provider(test, set_example_context_config):
    context = test['context']
    if 'provider_url' in test:
        target_provider_url = test['provider_url']
        provider = ctc.config.get_context_provider(context)
        actual_provider_url = provider['url']
        assert actual_provider_url == target_provider_url

