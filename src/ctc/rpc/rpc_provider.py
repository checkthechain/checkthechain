import os

from ctc import config_utils
from ctc import spec


def get_provider(provider: spec.ProviderSpec = None) -> spec.Provider:

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if isinstance(provider, dict):

        url = provider.get('url')
        if url is None:
            config = config_utils.get_config()
            default_provider = get_provider(config['export_provider'])
            if isinstance(default_provider, str):
                url = default_provider
            elif isinstance(provider, dict):
                url = default_provider['url']
            else:
                raise Exception('could not determine url')

        other_provider = get_provider(url)

        return {
            'type': other_provider['type'],
            'url': url,
            'session_kwargs': provider.get('session_kwargs', {}),
            'chunk_size': provider.get('chunk_size', None),
        }

    elif isinstance(provider, str):
        if provider.startswith('http'):
            return {
                'type': 'http',
                'url': provider,
                'session_kwargs': {},
                'chunk_size': None,
            }
        else:
            raise Exception('unknown provider format: ' + str(provider))
    else:
        raise Exception('unknown provider type: ' + str(type(provider)))


def get_provider_key(provider: spec.Provider) -> spec.ProviderKey:
    """return a unique identifier for provider within this process"""
    return (
        os.getpid(),
        provider['url'],
        tuple(provider['session_kwargs'].items()),
    )


def add_provider_parameters(
    provider: spec.ProviderSpec,
    parameters: spec.PartialProvider,
) -> spec.Provider:
    # TODO: decide whether parameters with value=None should be included
    provider = get_provider(provider)
    provider = dict(provider, **parameters)
    return provider

