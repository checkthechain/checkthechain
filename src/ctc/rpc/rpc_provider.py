from __future__ import annotations

import os
import typing

import ctc.config
from ctc import spec


def get_provider(provider: spec.ProviderReference = None) -> spec.Provider:

    if provider is None:

        # case: return default provider
        return ctc.config.get_default_provider()

    elif isinstance(provider, str):

        # case: provider specified as url
        if provider.startswith('http'):
            if ctc.config.has_provider(url=provider):
                return ctc.config.get_provider(url=provider)
            else:
                from ctc.config import config_defaults

                try:
                    network = config_defaults._sync_get_chain_id(provider)
                except Exception:
                    raise Exception('could not determine chain_id of provider')

                return {
                    'name': None,
                    'network': network,
                    'protocol': 'http',
                    'url': provider,
                    'session_kwargs': {},
                    'chunk_size': None,
                    'convert_reverts_to_none': False,
                }

        # case: provider specified as name in config
        elif ctc.config.has_provider(name=provider):
            return ctc.config.get_provider(name=provider)

        else:
            raise Exception('unknown provider format: ' + str(provider))

    elif isinstance(provider, dict):

        # case: partial provider
        if set(spec.provider_keys).issubset(set(provider.keys())):
            return provider  # type: ignore

        else:
            import copy

            selection_keys = ['name', 'network', 'protocol']
            if any(provider.get(key) is not None for key in selection_keys):
                base_provider = ctc.config.get_provider(
                    name=provider.get('name'),
                    network=provider.get('network'),
                    protocol=provider.get('protocol'),
                )
            else:
                base_provider = ctc.config.get_default_provider()

            data = {k: v for k, v in provider.items() if v is not None}
            if typing.TYPE_CHECKING:
                non_none_keys = typing.cast(spec.Provider, data)
            else:
                non_none_keys = data
            full_provider: spec.Provider = copy.copy(base_provider)
            full_provider.update(non_none_keys)  # type: ignore

            return full_provider

    else:
        raise Exception('unknown provider type: ' + str(type(provider)))


def get_provider_key(provider: spec.Provider) -> spec.ProviderKey:
    """return a unique identifier for provider within this process"""

    session_kwargs = provider.get('session_kwargs')
    if session_kwargs is None:
        session_kwargs = {}

    return (os.getpid(), provider['url'], tuple(session_kwargs.items()))


def get_provider_network(provider: spec.ProviderReference) -> spec.ChainId:
    if (
        provider is None
        or isinstance(provider, str)
        or 'network' not in provider
    ):
        provider = get_provider(provider)

    network = provider.get('network')
    if network is not None:
        if isinstance(network, int):
            return network
        else:
            from ctc import evm

            return evm.get_network_chain_id(network)
    else:
        raise spec.CouldNotDetermineNetwork('could not determine network')


def add_provider_parameters(
    provider: spec.ProviderReference,
    parameters: spec.PartialProvider,
) -> spec.Provider:
    import copy

    # TODO: decide whether parameters with value=None should be included
    provider = get_provider(provider)
    provider = copy.copy(provider)
    provider.update(parameters)  # type: ignore
    return provider
