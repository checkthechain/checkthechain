from __future__ import annotations

import functools
import os
import typing

from ctc import config
from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


def resolve_provider(
    provider: spec.ProviderReference,
    other_providers: typing.Mapping[str, spec.Provider] | None = None,
) -> spec.Provider:
    """try to lookup existing provider, and if it does not exist, create one"""
    if isinstance(provider, str):
        if other_providers is not None:
            candidates = list(other_providers.values())
        else:
            candidates = list(config.get_providers().values())
        try:
            # try provider name
            return find_provider(name=provider, candidates=candidates)
        except LookupError:
            try:
                # try provider url
                return find_provider(url=provider, candidates=candidates)
            except LookupError:
                # create new provider
                return create_provider(
                    url=provider, other_providers=other_providers
                )
    elif isinstance(provider, dict):
        return create_provider(other_providers=other_providers, **provider)
    else:
        raise Exception('unknown provider format: ' + str(type(provider)))


def create_provider(
    *,
    url: str | None = None,
    network: spec.NetworkReference | None = None,
    name: str | None = None,
    protocol: Literal['http', 'wss', 'ipc'] | None = None,
    session_kwargs: typing.Mapping[str, typing.Any] | None = None,
    chunk_size: int | None = None,
    convert_reverts_to_none: bool = True,
    validate_chain_id: bool = True,
    disable_batch_requests: bool = False,
    other_providers: typing.Mapping[str, spec.Provider] | None = None,
) -> spec.Provider:
    """create provider"""

    # url
    if url is None:
        if network is None:
            network = config.get_default_network()
        default_provider = config.get_network_default_provider(network)
        if default_provider is None:
            raise Exception('could not determine url for provider')
        url = default_provider['url']
    if not url.startswith('http'):
        if '://' in url:
            raise Exception('only http and https currently supported')

        # try http
        try:
            http_url = 'http://' + url
            _sync_get_chain_id(http_url)
            url = http_url
        except Exception:

            # try https
            try:
                https_url = 'https://' + url
                _sync_get_chain_id(https_url)
                url = https_url
            except Exception:
                raise Exception(
                    'provider url does not specify http or https and provider not responding to requests. make sure the url includes any relevant port numbers and http/https prefixes'
                )

    # network
    if network is None or validate_chain_id:
        actual_chain_id = _sync_get_chain_id(url)
    if network is None:
        network = actual_chain_id
    else:
        network = evm.get_network_chain_id(network)
        if validate_chain_id and network != actual_chain_id:
            raise Exception('provider network does not match given network')

    # name
    if other_providers is None:
        other_providers = config.get_providers()
    if name is not None:
        if name in other_providers:
            raise Exception(
                'provider with this name already exists, simply use provider=<provider_name> in arg or context'
            )
    if name is None:
        try:
            name = url.split('://')[1].split('/')[0] + '__' + str(network)
        except Exception:
            raise Exception(
                'could not determine name for provider, make sure url is formatted properly'
            )
        if name in other_providers:
            raise Exception(
                'could not determine unique name for new provider, specify a name argument'
            )

    # protocol
    if protocol is None:
        if url.startswith('http'):
            protocol = 'http'
        elif url.startswith('wss'):
            protocol = 'wss'
        elif url.startswith('ipc'):
            protocol = 'ipc'
        else:
            raise Exception('unknown protocol used by provider')

    if session_kwargs is None:
        session_kwargs = {}

    provider: spec.Provider = {
        'name': name,
        'network': network,
        'protocol': protocol,
        'url': url,
        'session_kwargs': session_kwargs,
        'chunk_size': chunk_size,
        'convert_reverts_to_none': convert_reverts_to_none,
        'disable_batch_requests': disable_batch_requests,
    }

    return provider


def find_provider(
    *,
    name: str | None = None,
    network: str | int | None = None,
    url: str | None = None,
    candidates: typing.Sequence[spec.Provider] | None = None,
) -> spec.Provider:
    """find provider that matches inputs from list of candidates

    if no candidates provided, use providers in config
    """

    from ctc import config
    from ctc.toolbox import search_utils

    if candidates is None:
        candidates = list(config.get_providers().values())

    # build query
    query: typing.MutableMapping[str, str | int] = {}
    if name is None and network is None and url is None:
        raise Exception('specify network name or network or url')
    if name is not None:
        query['name'] = name
    if network is not None:
        if isinstance(network, str):
            from ctc import evm

            network = evm.get_network_chain_id(network)
        query['network'] = network
    if url is not None:
        query['url'] = url

    entries = search_utils.get_matching_entries(
        sequence=candidates, query=query
    )
    if len(entries) == 1:
        return entries[0]
    elif len(entries) > 1:
        if network is not None:
            provider = config.get_network_default_provider(network=network)
            if provider is not None:
                return provider
        raise LookupError('too many candidate providers found')
    else:
        raise LookupError('could not detect suitable RPC provider')


# def get_provider(provider: spec.ProviderReference = None) -> spec.Provider:
#     import ctc.config

#     if provider is None:

#         # case: return default provider
#         return ctc.config.get_default_provider()

#     elif isinstance(provider, str):

#         # case: provider specified as url
#         if provider.startswith('http'):
#             if ctc.config.has_provider(url=provider):
#                 return ctc.config.get_provider(url=provider)
#             else:
#                 try:
#                     network = _sync_get_chain_id(provider)
#                 except Exception:
#                     raise Exception('could not determine chain_id of provider')

#                 return {
#                     'name': None,
#                     'network': network,
#                     'protocol': 'http',
#                     'url': provider,
#                     'session_kwargs': {},
#                     'chunk_size': None,
#                     'convert_reverts_to_none': False,
#                 }

#         # case: provider specified as name in config
#         elif ctc.config.has_provider(name=provider):
#             return ctc.config.get_provider(name=provider)

#         else:
#             raise Exception('unknown provider format: ' + str(provider))

#     elif isinstance(provider, dict):

#         # case: partial provider
#         if set(spec.provider_keys).issubset(set(provider.keys())):
#             return provider  # type: ignore

#         else:
#             import copy

#             selection_keys = ['name', 'network', 'protocol']
#             if any(provider.get(key) is not None for key in selection_keys):
#                 base_provider = ctc.config.get_provider(
#                     name=provider.get('name'),
#                     network=provider.get('network'),
#                     protocol=provider.get('protocol'),
#                 )
#             else:
#                 base_provider = ctc.config.get_default_provider()

#             data = {k: v for k, v in provider.items() if v is not None}
#             if typing.TYPE_CHECKING:
#                 non_none_keys = typing.cast(spec.Provider, data)
#             else:
#                 non_none_keys = data
#             full_provider: spec.Provider = copy.copy(base_provider)
#             full_provider.update(non_none_keys)  # type: ignore

#             return full_provider

#     else:
#         raise Exception('unknown provider type: ' + str(type(provider)))


def _get_provider_id(provider: spec.Provider) -> spec.ProviderId:
    """return a unique identifier for provider within this process"""

    session_kwargs = provider.get('session_kwargs')
    if session_kwargs is None:
        session_kwargs = {}

    return (os.getpid(), provider['url'], tuple(session_kwargs.items()))


@functools.lru_cache()
def _sync_get_chain_id(provider_url: str) -> int:
    """synchronously obtain chain_id of provider"""
    import json
    import urllib.request

    data = {'jsonrpc': '2.0', 'method': 'eth_chainId', 'params': [], 'id': 1}
    encoded_data = json.dumps(data).encode()
    request = urllib.request.Request(
        provider_url,
        data=encoded_data,
        headers={
            'User-Agent': 'python3',
            'Content-Type': 'application/json',
        },
    )
    response = urllib.request.urlopen(request, timeout=5)
    response_data = json.loads(response.read().decode())
    raw_chain_id = response_data['result']
    return evm.binary_convert(raw_chain_id, 'integer')

