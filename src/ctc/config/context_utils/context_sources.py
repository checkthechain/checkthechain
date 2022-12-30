from __future__ import annotations

from ctc import spec

from . import context_validate


def get_context_chain_id(context: spec.Context) -> spec.ChainId:
    """get chain_id of a given context"""
    context_validate._validate_context(context)
    chain_id, provider = _get_context_network_and_provider(context=context)
    return chain_id


def get_context_provider(context: spec.Context) -> spec.Provider:
    """get provider of a given context"""
    context_validate._validate_context(context)
    chain_id, provider = _get_context_network_and_provider(context=context)
    if provider is None:
        raise Exception('context does not specify any possible provider')
    return provider


def _get_context_network_and_provider(
    context: spec.Context,
) -> tuple[spec.ChainId, spec.Provider | None]:

    from ctc import config
    from ctc import rpc

    if context is None:
        # case: no context provided
        default_network = config.get_default_network()
        if default_network is None:
            raise Exception('no default network specified')
        else:
            chain_id = default_network

        provider = _chain_id_to_provider(chain_id)

    elif isinstance(context, int):
        # case: context is only a chain_id
        for chain_id in config.get_config_networks().keys():
            if chain_id == context:
                break
        else:
            raise Exception(
                'could not find provider for chain_id = ' + str(context)
            )
        provider = _chain_id_to_provider(chain_id)

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
            provider = _chain_id_to_provider(chain_id)

        else:
            # subcase: neither provider nor network are given
            default_network = config.get_default_network()
            if default_network is None:
                raise Exception('no default network specified')
            else:
                chain_id = default_network
            provider = _chain_id_to_provider(chain_id)

    else:
        raise Exception('unknown context format: ' + str(type(context)))

    return chain_id, provider


def _chain_id_to_provider(chain_id: spec.ChainId) -> spec.Provider | None:
    from ctc import rpc

    try:
        return rpc.get_provider({'network': chain_id})
    except LookupError:
        return None

