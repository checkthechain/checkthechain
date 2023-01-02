from __future__ import annotations

from ctc import spec
from . import context_caches
from . import context_sources


def create_user_input_context(
    *,
    provider: str | None = None,
    network: str | spec.NetworkReference | None = None,
    cache: spec.ContextCacheShorthand = None,
) -> spec.Context:

    if isinstance(network, str) and network.isnumeric():
        network = int(network)

    context: spec.ShorthandContext = {
        'provider': provider,
        'network': network,
        'cache': cache,
    }

    return context


def normalize_context(context: spec.Context) -> spec.NormalizedContext:
    network, provider = context_sources._get_context_chain_id_and_provider(
        context
    )
    cache_rules = context_caches._extract_context_cache_rules(context=context)
    return {
        'network': network,
        'provider': provider,
        'cache': cache_rules,
    }


def update_context(
    context: spec.Context,
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
    merge_provider: spec.PartialProvider | None = None,
    cache: spec.ContextCacheShorthand = None,
) -> spec.NormalizedContext:

    new_context = normalize_context(context)

    if network is not None:
        new_context['network'] = network
    if provider is not None:
        new_context['provider'] = provider
    if merge_provider is not None:
        from ctc import rpc

        if provider is None:
            new_context['provider'] = rpc.resolve_provider(merge_provider)
        else:
            provider = rpc.resolve_provider(provider)
            new_context['provider'] = dict(provider, **merge_provider)  # type: ignore

    if cache is not None:
        cache_rules = context_caches._extract_context_cache_rules(
            context_cache=cache
        )
        new_context['cache'] = list(cache_rules) + list(new_context['cache'])

    return new_context

