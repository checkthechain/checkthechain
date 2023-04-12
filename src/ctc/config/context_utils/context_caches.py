from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import toolsql

from ctc import spec
from .. import config_values
from . import context_sources


def get_context_db_config(
    *,
    schema_name: str,
    context: spec.Context,
) -> toolsql.DBConfig:
    """get db_config of backend schema cache for a given context"""

    if not spec.is_schema_name(schema_name):
        raise Exception('not a valid schema name: ' + str(schema_name))
    backend = get_context_cache_backend(
        schema_name=schema_name, context=context
    )
    if backend is None:
        raise Exception(
            'no backend active for current context, cannot retrieve db_config'
        )
    return config_values.get_db_config(backend)


def get_context_cache_backend(
    *,
    schema_name: spec.db_types.SchemaName,
    context: spec.Context,
) -> str | None:
    """get backend schema cache for a given context"""
    backend, _read, _write = _get_context_cache_settings(
        schema_name=schema_name,
        context=context,
    )
    return backend


def get_context_cache_read_write(
    *,
    schema_name: str,
    context: spec.Context,
) -> tuple[bool, bool]:
    """get settings (read, write) of schema for a given context"""

    if not spec.is_schema_name(schema_name):
        raise Exception('not a valid schema name: ' + str(schema_name))
    _backend, read, write = _get_context_cache_settings(
        schema_name=schema_name,
        context=context,
    )

    return read, write


def _get_context_cache_settings(
    schema_name: spec.db_types.SchemaName,
    context: spec.Context,
) -> tuple[str | None, bool, bool]:
    """get settings (backend, read, write) of schema for a given context"""

    from ctc import config

    # get chain id if schema is network-related
    if schema_name in spec.network_schema_names:
        chain_id = context_sources.get_context_chain_id(context)
    else:
        chain_id = None

    # assemble rules from context and config
    config_rules = config.get_context_cache_rules()
    context_rules = _extract_context_cache_rules(context=context)
    rules = [rule for rl in [context_rules, config_rules] for rule in rl]

    return _resolve_context_cache_rules(
        rules=rules,
        chain_id=chain_id,
        schema_name=schema_name,
    )


def _extract_context_cache_rules(
    *,
    context_cache: spec.ContextCacheShorthand = None,
    context: spec.Context = None,
) -> typing.Sequence[spec.ContextCacheRule]:
    """convert a context's cache to a list of cache rules

    - this does not depend on the context_cache_rules of the config
    - this does depends on which networks, providers, or backends are in config
    """

    if context_cache is None:
        if isinstance(context, dict):
            context_cache = context.get('cache')
        else:
            return []

    if context_cache is None:
        return []
    elif isinstance(context_cache, bool):
        return [
            {'read': context_cache, 'write': context_cache},
        ]
    elif isinstance(context_cache, str):
        return [
            {'backend': context_cache},
        ]
    elif isinstance(context_cache, dict):
        keys = set(context_cache.keys())

        if keys.issubset({'filter', 'read', 'write', 'backend'}):
            # case: non-nested cache
            return [context_cache]  # type: ignore

        else:
            # case: nested caches
            rules = []
            for key, value in context_cache.items():
                rule = _create_nested_cache_rule(key, value)  # type: ignore
                if rule is not None:
                    rules.append(rule)

            return rules

    elif isinstance(context_cache, list):
        return context_cache
    else:
        raise Exception('unknown format for context_cache')


def _create_nested_cache_rule(
    key: str | int,
    value: None | bool | str | spec.ContextCacheRule,
) -> spec.ContextCacheRule | None:
    """assemble a single cache rule from within a shorthand nested cache spec"""

    from ctc import config

    # determine rule filter
    if key in spec.schema_names:
        filter: spec.ContextCacheFilter = {'schema': key}  # type: ignore
    elif isinstance(key, int):
        filter = {'chain_id': key}
    elif key in config.get_cache_backends():
        filter = {'backend': key}
    else:
        for chain_id, network_metadata in config.get_config_networks().items():
            if network_metadata['name'] == key:
                filter = {'chain_id': chain_id}
                break
        else:
            raise Exception('unknown cache identifier: ' + str(key))

    # determine rule settings
    if value is None:
        return None
    elif isinstance(value, bool):
        return {'filter': filter, 'read': value, 'write': value}
    elif isinstance(value, str):
        return {'filter': filter, 'backend': value}
    elif isinstance(value, dict):
        if not set(value.keys()).issubset({'backend', 'read', 'write'}):
            raise Exception('invalid keys for nested cache config')
        rule = value.copy()
        rule['filter'] = filter
        return rule
    else:
        raise Exception('unknown value for cache: ' + str(value))


def _resolve_context_cache_rules(
    rules: typing.Sequence[spec.ContextCacheRule],
    *,
    chain_id: spec.ChainId | None,
    schema_name: spec.SchemaName,
) -> tuple[str | None, bool, bool]:
    """get settings (backend, read, write) of schema for a given rule list"""

    backend: str | None = None
    read: bool | None = None
    write: bool | None = None

    # perform first pass to determine backend
    for rule in rules:
        if _does_cache_rule_apply(
            rule=rule, chain_id=chain_id, schema_name=schema_name
        ):
            if rule.get('backend') is not None:
                backend = rule['backend']
                break
    if backend is None:
        raise Exception('could not determine backend for cache')

    # perform second pass to determine read+write settings
    for rule in rules:
        if _does_cache_rule_apply(
            rule=rule,
            chain_id=chain_id,
            schema_name=schema_name,
            backend=backend,
        ):
            if read is None and rule.get('read') is not None:
                read = rule['read']
            if write is None and rule.get('write') is not None:
                write = rule['write']
    if read is None:
        raise Exception('could not determine read setting for cache')
    if write is None:
        raise Exception('could not determine write setting for cache')

    return backend, read, write


def _does_cache_rule_apply(
    rule: spec.ContextCacheRule,
    *,
    chain_id: spec.ChainId | None,
    schema_name: spec.SchemaName,
    backend: str | None = None,
) -> bool:
    """return whether a given context cache rule applies to given inputs"""

    # filter according to scoping rules
    filter = rule.get('filter')
    if filter is None:
        return True
    if filter.get('chain_id') is not None and filter['chain_id'] != chain_id:
        return False
    if filter.get('schema') is not None and filter['schema'] != schema_name:
        return False
    if filter.get('backend') is not None and filter['backend'] != backend:
        return False

    return True

