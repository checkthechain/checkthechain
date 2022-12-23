"""
# Context
- every `ctc` function that queries data can specify a `context` argument
- `context` can specify the data source and various query behaviors
- for example:
    - specify that a query should be sent to Polygon, Arbitrum, or Mainnet
    - specify which RPC provider to use if multiple are avaiable
    - specify whether to read results from cache, or write results to cache


## Context Format
- `context` can be a `dict`, `str`, or `int`
    - `dict`: map of context options
    - `int`: the chain id of an EVM network
    - `str`: one of
        1. the name of an EVM network
        2. the name of an RPC provider
        3. the url of an RPC provider
- a `context` `dict` has many possible options
    - see sections below for possible keys and their behaviors
    - unspecified keys will use default values


## Comparison to old `ctc` design
- `context` replaces all of the following arguments:
    - `provider`
    - `network`
    - `use_db`
    - `read_db`
    - `write_db`
- `context` has the following advantages:
    - simplifies `ctc` API and makes it easier to use
    - allows granular configuration of multiple caches
    - future proofs many extensions of cache config


# Context Attributes

## Provider / Network
- Functions that acquire on-chain data can specify `provider` and/or `network`
- if both are specified, they should be compatible
- a context currently describes a query environment for a single network
    - multiple networks require multiple contexts
    - future versions of `ctc` may use multi-network contexts

## Caches
- For functions that use a cache, context can contain the following
    - `cache`: attempt to read from and write to cache
    - `read_cache`: attempt to read result from cache
    - `write_cache`: write result to cache
- default settings
    - for each cache field that equals `True`, use the default cache in config
    - if cache is not specified, use value in config
    - if `read_cache` is not specified, use `cache` value
    - if `write_cache` is not specified, use `cache` value
- each of the following is valid
    context={'cache': True}
    context={'read_cache': False}
    context={'write_cache': False}
    context={'read_cache': True, 'write_cache': False}
    context={'read_cache': False, 'write_cache': True}
    context={'cache': 'local_sqlite'}
    context={'cache': 'local_postgres'}
    context={'cache': 'cloud'}
    context={'cache': {'blocks': True, 'transactions': False}}
    context={'cache': {'blocks': 'local_sqlite', 'transactions': False}}
    context={'cache': {'blocks': 'local_sqlite', 'transactions': 'cloud'}}


## Future-proofing
- specify additional primary data sources
    - BigQuery
    - theGraph
- specify multiple caches
- specify communication protocols
    - websocket
    - ipc
- specify multiple providers
    - round robin rotate between them?
- be able to specify no provider should be used, only cache


## TODO
- add check that there is no conflicts between
    - provider names
    - network names
    - cache names
"""

from __future__ import annotations

import typing

from ctc import config
from ctc import spec
from ctc import rpc


def get_context_chain_id(context: spec.Context) -> spec.ChainId:
    """get chain_id of a given context"""
    chain_id, provider = _get_context_network_and_provider(context=context)
    return chain_id


def get_context_provider(context: spec.Context) -> spec.Provider:
    """get provider of a given context"""
    chain_id, provider = _get_context_network_and_provider(context=context)
    return provider


def get_schema_cache_context(
    *,
    schema_name: spec.SchemaName,
    chain_id: spec.ChainId | None,
    context: spec.Context,
) -> tuple[spec.CacheId | None, bool, bool]:
    """get cache_id, read_cache, and write_cache according to given context

    cache_id==None indicates no cache
    """
    if chain_id is None:
        from ctc import db

        if schema_name in db.get_network_schema_names():
            chain_id = config.get_default_network()
    cache = _get_context_cache_config(
        schema_name=schema_name,
        chain_id=chain_id,
        context=context,
    )
    return cache['cache'], cache['read_cache'], cache['write_cache']


def get_full_context(context: spec.Context) -> spec.FullContext:
    """expand given context to its full context with all fields shown

    it is less computationally expensive to retrieve partial contexts
    """

    chain_id, provider = _get_context_network_and_provider(context)
    cache = _get_all_context_cache_configs(context=context, chain_id=chain_id)

    return {
        'network': chain_id,
        'provider': provider,
        'cache': cache,
    }


def _get_context_network_and_provider(
    context: spec.Context,
) -> tuple[spec.ChainId, spec.Provider]:

    if context is None:
        # case: no context provided
        default_network = config.get_default_network()
        if default_network is None:
            raise Exception('no default network specified')
        else:
            chain_id = default_network
        provider = rpc.get_provider({'network': chain_id})

    elif isinstance(context, int):
        # case: context is only a chain_id
        for chain_id in config.get_config_networks().keys():
            if chain_id == context:
                break
        else:
            raise Exception(
                'could not find provider for chain_id = ' + str(context)
            )
        provider = rpc.get_provider({'network': chain_id})

    elif isinstance(context, str):
        # case: context is a network name, provider name, or provider url
        for chain_id, network_metadata in config.get_config_networks().items():
            if network_metadata.get('name') == context:
                provider = rpc.get_provider({'network': chain_id})
                break
        else:
            provider = rpc.get_provider(context)
        chain_id = provider['network']

    elif isinstance(context, dict):
        # case: context is a dict

        if context.get('provider') is not None:
            # subcase: provider is given
            provider = rpc.get_provider(context['provider'])
            chain_id = provider['network']

        elif context.get('network') is not None:
            # subcase: network is given
            context_network = context['network']
            for (
                chain_id,
                network_metadata,
            ) in config.get_config_networks().items():
                if isinstance(context_network, int):
                    if context_network == chain_id:
                        break
                elif isinstance(context_network, str):
                    if context_network == network_metadata['name']:
                        break
                else:
                    raise Exception(
                        'unknown network format: ' + str(context_network)
                    )
            provider = rpc.get_provider({'network': chain_id})

        else:
            # subcase: neither provider nor network are given
            default_network = config.get_default_network()
            if default_network is None:
                raise Exception('no default network specified')
            else:
                chain_id = default_network
            provider = rpc.get_provider({'network': chain_id})

    else:
        raise Exception('unknown context format: ' + str(type(context)))

    return chain_id, provider


def _get_all_context_cache_configs(
    context: spec.Context,
    chain_id: spec.ChainId | None,
) -> spec.MultiCacheContext:

    from ctc import db

    schema_names: tuple[spec.SchemaName] = db.get_generic_schema_names()
    if chain_id is not None:
        schema_names = schema_names + db.get_network_schema_names()  # type: ignore

    cache_configs: spec.MutableMultiCacheContext = {}
    for schema_name in schema_names:
        cache_configs[schema_name] = _get_context_cache_config(
            schema_name=schema_name,
            chain_id=chain_id,
            context=context,
        )

    return cache_configs


def _get_context_cache_config(
    *,
    context: spec.Context,
    chain_id: spec.ChainId | None,
    schema_name: spec.SchemaName,
) -> spec.SingleCacheContext:

    cache_config = config.get_schema_cache_config(
        schema_name=schema_name,
        chain_id=chain_id,
    )

    # chain_id already determined, so cache only affected if context also a dict
    if isinstance(context, dict):
        import copy

        cache_config = copy.copy(cache_config)

        cache = context.get('cache')

        # case: read_cache or write_cache specified
        keys: typing.Sequence[typing.Literal['read_cache', 'write_cache']] = [
            'read_cache',
            'write_cache',
        ]
        # key: typing.Literal['read_cache', 'write_cache']
        # for key in ['read_cache', 'write_cache']:
        for key in keys:
            value = context.get(key)
            if value is None:
                continue
            if cache is not None:
                raise Exception(
                    'context should not specify both cache and read_cache'
                )
            if isinstance(value, bool):
                cache_config[key] = value
            else:
                raise Exception(
                    'invalid type for ' + key + ': ' + str(type(value))
                )

        # case: cache is specified
        if cache is not None:

            # subcase: cache is a bool
            if isinstance(cache, bool):
                cache_config['read_cache'] = cache
                cache_config['write_cache'] = cache

            # subcase: cache is a str
            elif isinstance(cache, str):
                cache_config['cache'] = cache
                cache_config['read_cache'] = True
                cache_config['write_cache'] = True

            # subcase: cache is a dict
            elif isinstance(cache, dict):

                cache_keys = ['read_cache', 'write_cache', 'cache']
                if any(key in cache for key in cache_keys):
                    raise Exception(
                        'wrong level of nesting used for cache context'
                    )

                if schema_name in cache:
                    if isinstance(cache[schema_name], bool):
                        cache_config['read_cache'] = cache[schema_name]
                        cache_config['write_cache'] = cache[schema_name]

                    elif isinstance(cache[schema_name], str):
                        cache_config['cache'] = cache[schema_name]
                        cache_config['read_cache'] = True
                        cache_config['write_cache'] = True

                    elif isinstance(cache[schema_name], dict):
                        cache_config.update(cache[schema_name])

                    else:
                        raise Exception(
                            'unknown type for cache: '
                            + str(type(cache[schema_name]))
                        )

            else:
                raise Exception('unknown type for cache: ' + str(type(cache)))

    return cache_config

