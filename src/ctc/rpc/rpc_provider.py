import copy
import os

from ctc import config_utils
from ctc import spec


def get_provider(provider: spec.ProviderSpec) -> spec.Provider:

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if isinstance(provider, dict):
        for key in ['type', 'url', 'session_kwargs', 'chunk_size']:
            if key not in provider:
                provider = copy.copy(provider)
        if 'type' not in provider:
            if 'url' not in provider:
                config = config_utils.get_config()
                default_provider = get_provider(config['export_provider'])
            else:
                default_provider = get_provider(provider['url'])
            provider['url'] = default_provider['url']
            provider['type'] = default_provider['type']
        if 'url' not in provider:
            raise Exception('malformed provider spec')
        provider.setdefault('session_kwargs', {})
        provider.setdefault('chunk_size', None)

    elif isinstance(provider, str):
        if provider.startswith('http'):
            provider = {
                'type': 'http',
                'url': provider,
                'session_kwargs': {},
                'chunk_size': None,
            }
        else:
            raise Exception('unknown provider format: ' + str(provider))
    else:
        raise Exception('unknown provider type: ' + str(type(provider)))

    # validate provider
    assert isinstance(provider, dict)
    assert 'type' in provider
    assert 'url' in provider
    assert 'session_kwargs' in provider
    assert 'chunk_size' in provider

    return provider


def get_provider_key(provider: spec.Provider) -> spec.ProviderKey:
    """return a unique identifier for provider within this process"""
    return (
        os.getpid(),
        provider['url'],
        tuple(provider['session_kwargs'].items()),
    )

