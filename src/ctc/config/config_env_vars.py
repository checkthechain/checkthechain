from __future__ import annotations

import os
import typing

from . import context_utils
from . import config_spec


def _add_config_env_vars(
    config: typing.MutableMapping[str, typing.Any]
) -> typing.MutableMapping[str, typing.Any]:
    config = dict(config)
    parse_env_network_and_provider(config)
    parse_env_cache(config)
    return config


def parse_env_network_and_provider(
    config: typing.MutableMapping[str, typing.Any]
) -> None:
    """
    Possible actions
    - set existing provider as default
    - create new provider and use it as default
    """

    # parse env network
    env_network = os.environ.get(config_spec.network_env_var)
    env_chain_id: None | int = None
    if env_network is not None:
        if env_network.isnumeric():
            env_chain_id = int(env_network)
        else:
            for chain_id, network_metadata in config['networks'].items():
                if network_metadata['name'] == env_network:
                    env_chain_id = chain_id
                    break
            else:
                raise Exception('unknown network: ' + str(env_network))

    # parse env provider
    env_provider_name: None | str = None
    env_provider_chain_id: None | int = None
    env_provider = os.environ.get(config_spec.provider_env_var)
    if env_provider is not None and env_provider != '':
        if env_provider in config['providers']:
            env_provider_name = env_provider
            env_provider_chain_id = config['providers'][env_provider]['network']
        else:
            for provider_name, provider in config['providers'].items():
                # if env_provider already in config, use it
                if provider['url'] == env_provider:
                    env_provider_name = provider_name
                    env_provider_chain_id = provider['network']
                    break
            else:
                # if env_provider not in config, make new provider
                from ctc import rpc

                if env_provider.startswith('{'):
                    import ast

                    provider_shorthand = ast.literal_eval(env_provider)
                else:
                    provider_shorthand = {'url': env_provider}

                try:
                    provider = rpc.resolve_provider(
                        provider_shorthand,
                        other_providers=config.get('providers'),
                    )
                    env_provider_name = provider['name']
                    env_provider_chain_id = provider['network']
                    config['providers'][env_provider_name] = provider

                except LookupError:
                    import warnings

                    warnings.warn(
                        'invalid provider specified in CTC_PROVIDER environment variable, skipping'
                    )

    # set default provider
    if env_chain_id is not None and env_provider_chain_id is not None:
        if env_chain_id == env_provider_chain_id:
            config['default_network'] = env_chain_id
        else:
            raise Exception(
                'network of CTC_NETWORK does not match network of CTC_PROVIDER'
            )
    elif env_chain_id is not None:
        config['default_network'] = env_chain_id
    elif env_provider_chain_id is not None:
        config['default_network'] = env_provider_chain_id

    # set provider
    if env_provider_name is not None:
        config['default_providers'][env_provider_chain_id] = env_provider_name


def parse_env_cache(config: typing.MutableMapping[str, typing.Any]) -> None:

    env_cache = os.environ.get(config_spec.cache_env_var)
    if env_cache is not None and env_cache != '':
        import ast

        cache_shorthand = ast.literal_eval(env_cache)
        rules = context_utils.context_caches._extract_context_cache_rules(
            context_cache=cache_shorthand
        )
        config['context_cache_rules'] = rules + config['context_cache_rules']

