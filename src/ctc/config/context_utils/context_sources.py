from __future__ import annotations

from ctc import evm
from ctc import spec

from .. import config_values
from . import context_validate


def get_context_chain_id(context: spec.Context) -> spec.ChainId:
    """get chain_id of a given context"""

    context_validate._validate_context(context)
    chain_id, provider = _get_context_chain_id_and_provider(context=context)
    return chain_id


def get_context_network_name(context: spec.Context) -> str:
    """get network_name of a given context"""
    chain_id = get_context_chain_id(context)
    return evm.get_network_name(chain_id)


def get_context_provider(context: spec.Context) -> spec.Provider | None:
    """get provider of a given context"""

    context_validate._validate_context(context)
    chain_id, provider = get_context_chain_id_and_provider(context=context)
    return provider


def get_context_chain_id_and_provider(
    context: spec.Context,
) -> tuple[spec.ChainId, spec.Provider | None]:
    """get chain_id and provider of a given context"""

    from ctc import rpc

    context_validate._validate_context(context)
    chain_id, provider = _get_context_chain_id_and_provider(context=context)

    if provider is not None:
        return chain_id, provider
    else:
        try:
            provider = rpc.find_provider(network=chain_id)
        except LookupError:
            pass
        return chain_id, provider


def _get_context_chain_id_and_provider(
    context: spec.Context,
) -> tuple[spec.ChainId, spec.Provider | None]:

    from ctc import rpc

    if context is None:
        # case: no context provided
        return config_values.get_default_network(), None

    elif isinstance(context, int):
        # case: context is a chain_id
        return context, None

    elif isinstance(context, str):
        # case: context is a network name, provider name, or provider url
        try:
            # try to resolve as network name
            return evm.get_network_chain_id(context), None
        except LookupError:
            # try to resolve as provider
            provider = rpc.resolve_provider(context)
            return provider['network'], provider

    elif isinstance(context, dict):
        # case: context is a dict
        context_network = context.get('network')
        context_provider = context.get('provider')

        if context_provider is not None:
            # subcase: provider is given
            provider = rpc.resolve_provider(context_provider)
            if (
                context_network is not None
                and evm.get_network_chain_id(context_network) != provider['network']
            ):
                raise Exception('context provider does not match network')
            return provider['network'], provider

        elif context_network is not None:
            # subcase: network is given
            return evm.get_network_chain_id(context_network), None

        else:
            # subcase: neither provider nor network are given
            return config_values.get_default_network(), None

    raise Exception('unknown context format: ' + str(type(context)))

