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
    - non-rpc interface to erigon or reth
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

from ctc import config
from ctc import spec
from ctc import rpc


def get_context_chain_id(context: spec.Context) -> spec.ChainId:
    """get chain_id of a given context"""
    _validate_context(context)
    chain_id, provider = _get_context_network_and_provider(context=context)
    return chain_id


def get_context_provider(context: spec.Context) -> spec.Provider:
    """get provider of a given context"""
    _validate_context(context)
    chain_id, provider = _get_context_network_and_provider(context=context)
    return provider


def get_context_schema_cache(
    *,
    schema_name: spec.SchemaName,
    context: spec.Context,
    chain_id: spec.ChainId | None = None,
) -> tuple[spec.CacheBackend | None, bool, bool]:
    """get cache backend, read, and write according to given context

    backend==None indicates no cache
    """

    _validate_context(context)

    if chain_id is None:
        from ctc import db

        if schema_name in db.get_network_schema_names():
            chain_id = config.get_default_network()

    cache = _get_context_cache_config(
        schema_name=schema_name,
        chain_id=chain_id,
        context=context,
    )

    return cache['backend'], cache['read'], cache['write']


def get_full_context(context: spec.Context) -> spec.FullContext:
    """expand given context to its full context with all fields shown

    this is more computationally expensive than retrieving partial contexts
    """

    _validate_context(context)

    chain_id, provider = _get_context_network_and_provider(context)
    cache = _get_all_context_cache_configs(context=context, chain_id=chain_id)

    return {
        'network': chain_id,
        'provider': provider,
        'cache': cache,
    }


def _validate_context(context: spec.Context) -> None:
    """validate user-given context specification"""

    if isinstance(context, dict):
        if not set(context.keys()).issubset(spec.context_keys):
            raise Exception(
                'invalid keys for context: '
                + str(set(context.keys()) - set(spec.context_keys))
                + ', valid keys are: '
                + str(set(spec.context_keys))
            )


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
    config_cache = config.get_schema_cache_config(
        schema_name=schema_name,
        chain_id=chain_id,
    )
    if isinstance(context, dict):
        return _resolve_context_cache(
            output=config_cache.copy(),
            context_cache=context.get('cache'),
            schema_name=schema_name,
        )
    else:
        return config_cache


def _resolve_context_cache(
    *,
    output: spec.SingleCacheContext,
    context_cache: spec.CacheContextShorthand | None,
    schema_name: spec.SchemaName,
    allow_nesting: bool = True,
) -> spec.SingleCacheContext:

    if context_cache is None:
        return output
    elif isinstance(context_cache, bool):
        output['read'] = context_cache
        output['write'] = context_cache
        return output
    elif isinstance(context_cache, str):
        output['backend'] = context_cache
        return output
    elif isinstance(context_cache, dict):
        keys = set(context_cache.keys())
        if keys.issubset(spec.context_cache_keys):
            for key in spec.context_cache_keys:
                if context_cache.get(key) is not None:
                    output[key] = context_cache[key]
            return output
        elif allow_nesting:
            from ctc import db

            if not keys.issubset(db.get_all_schema_names()):
                raise Exception('some keys in cache spec are unknown')
            return _resolve_context_cache(
                output=output,
                context_cache=context_cache.get(schema_name),
                schema_name=schema_name,
                allow_nesting=False,
            )

    raise Exception('unknown cache format: ' + str(context_cache))

