"""
# Context
- every `ctc` function that queries data can specify a `context` argument
- for example:
    - specify that a query should be sent to Polygon, Arbitrum, or Mainnet
    - specify which RPC provider to use if multiple are avaiable
    - specify whether to read results from cache, or write results to cache
- `context` can specify the data source and various query behaviors


## Context Format
- `context` can be a `dict`, `str`, or `int`
    - `dict`: map of context options
    - `str`: either the name of an EVM network or the name of an RPC provider
    - `int`: the chain id of an EVM network
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
    - simplifies `ctc` API and minimize cognitive overhead for end user
    - allow granular configuration of multiple caches
    - future proof for specifying additional data sources like BigQuery or theGraph


## Provider / Network
- Functions that acquire on-chain data can specify `provider` and/or `network`
- if both are specified, they should be compatible


## Cache Context
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


## What is and is not a context
- a context describes a query environment for a single network
    - multiple networks require multiple contexts


## TODO
- add check that there is no conflicts between
    - provider names
    - network names
    - cache names
"""
from __future__ import annotations

from ctc import config
from ctc import spec
from ctc import rpc


def get_full_context(context: spec.Context) -> spec.FullContext:

    # determine network and provider
    if context is None:
        chain_id = config.get_default_network()
        provider = rpc.get_provider({'network': chain_id})

    elif isinstance(context, int):
        for chain_id in config.get_config_networks().keys():
            if chain_id == context:
                break
        else:
            raise Exception(
                'could not find provider for chain_id = ' + str(context)
            )
        provider = rpc.get_provider({'network': chain_id})

    elif isinstance(context, str):
        for chain_id, network_metadata in config.get_config_networks().items():
            if network_metadata.get('name') == context:
                provider = rpc.get_provider({'network': chain_id})
                break
        else:
            provider = rpc.get_provider(context)
        chain_id = provider['network']

    elif isinstance(context, dict):
        if context.get('provider') is not None:
            provider = rpc.get_provider(context['provider'])
            chain_id = provider['network']
        elif context.get('network') is not None:
            context_network = context['network']
            for chain_id, network_metadata in config.get_config_networks().items():
                if isinstance(context_network, int):
                    if context_network == chain_id:
                        break
                elif isinstance(context_network, str):
                    if context_network == network_metadata['name']:
                        break
            provider = rpc.get_provider({'network': chain_id})
        else:
            default_network = config.get_default_network()
            if default_network is None:
                raise Exception('no default network specified')
            else:
                chain_id
            provider = rpc.get_provider({'network': chain_id})

    else:
        raise Exception('unknown context format: ' + str(type(context)))

    # determine cache attributes
    if isinstance(context, dict):
        cache = config.get_network_cache_config(chain_id=chain_id)
        read_cache = context.get('read_cache')
        write_cache = context.get('write_cache')
        if read_cache is not None or write_cache is not None:
            new_cache = {}
            for schema_name, cache_context in cache.items():
                new_cache_context = dict(cache_context)
                if read_cache is not None:
                    new_cache_context['read_cache'] = read_cache
                if write_cache is not None:
                    new_cache_context['write_cache'] = write_cache
                new_cache[schema_name] = new_cache_context
            cache = new_cache
    else:
        cache = config.get_network_cache_config(chain_id=chain_id)

    return {
        'network': chain_id,
        'provider': provider,
        'cache': cache,
    }


def get_context_provider(context: spec.Context) -> spec.Provider:
    if context is None:
        return config.get_default_provider()
    elif isinstance(context, int):
        for chain_id in config.get_config_networks().keys():
            if chain_id == context:
                return rpc.get_provider({'network': context})
        raise Exception(
            'could not find provider for chain_id = ' + str(context)
        )
    elif isinstance(context, str):
        # check for networks
        for chain_id, network_metadata in config.get_config_networks().items():
            if network_metadata.get('name') == context:
                return rpc.get_provider({'network': chain_id})

        # check for providers
        return rpc.get_provider(context)
    elif isinstance(context, dict):
        if context.get('network') is not None:
            return rpc.get_provider({'network': context['network']})
        elif context.get('provider') is not None:
            return rpc.get_provider(context['provider'])
        else:
            return config.get_default_provider()
    else:
        raise Exception('unknown context format')


def get_context_chain_id(context: spec.Context) -> spec.ChainId:
    full_context = get_full_context(context)
    return full_context['network']


def get_cache_context(
    schema_name: spec.SchemaName | None,
    context: spec.Context,
) -> tuple[spec.CacheId | None, bool, bool]:
    """get cache_id, read_cache, and write_cache according to given context"""

    if not isinstance(context, dict):
        # if context not a dict, default cache behavior for network
        chain_id = get_context_chain_id(context)
        cache_config = config.get_cache_config(
            schema_name=schema_name,
            chain_id=chain_id,
        )
        return (
            cache_config['cache'],
            cache_config['read_cache'],
            cache_config['write_cache'],
        )

    else:
        # if context is a dict, determine behavior from context cache fields

        # get cache fields
        context_cache = context.get('cache')
        read_cache = context.get('read_cache')
        write_cache = context.get('write_cache')
        if isinstance(context_cache, bool) and (write_cache or read_cache):
            raise Exception(
                'if specifying write_cache=True or read_cache=True,'
                'should not specify boolean value for cache'
            )

        # determine read_cache if not specified
        if read_cache is None:
            if context_cache is not None:
                # if context parameter specified, use it
                if isinstance(context_cache, str):
                    read_cache = True
                elif isinstance(context_cache, bool):
                    read_cache = context_cache
                else:
                    raise Exception('unknown context cache format given')
            else:
                # otherwise use default read_cache value
                chain_id = get_context_chain_id(context)
                config_cache = config.get_cache_config(
                    schema_name=schema_name,
                    chain_id=chain_id,
                )
                read_cache = config_cache['write_cache']

        # determine write_cache if not specified
        if write_cache is None:
            if context_cache is not None:
                # if context parameter specified, use it
                if isinstance(context_cache, str):
                    write_cache = True
                elif isinstance(context_cache, bool):
                    write_cache = context_cache
                else:
                    raise Exception('unknown context cache format given')
            else:
                # otherwise use default write_cache value
                chain_id = get_context_chain_id(context)
                config_cache = config.get_cache_config(
                    schema_name=schema_name,
                    chain_id=chain_id,
                )
                write_cache = config_cache['write_cache']

        # determine cache id
        if isinstance(context_cache, str):
            cache_id = context_cache
        elif isinstance(context_cache, bool):
            if not context_cache:
                cache_id = None
            else:
                chain_id = get_context_chain_id(context)
                config_cache = config.get_cache_config(
                    schema_name=schema_name,
                    chain_id=chain_id,
                )
                cache_id = config_cache['cache']
        else:
            raise Exception('unknown format for context cache')

        return cache_id, read_cache, write_cache

