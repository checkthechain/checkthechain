from __future__ import annotations

import typing
import os

from ctc import spec
from ctc.toolbox import search_utils
from . import config_read


def get_config_version() -> str:
    return config_read.get_config()['version']


def get_data_dir() -> str:
    data_dir = config_read.get_config()['data_dir']
    data_dir = os.path.expanduser(data_dir)
    return data_dir


def get_reports_dir() -> str:
    return os.path.join(get_data_dir(), 'notebooks')


def get_networks() -> dict[spec.NetworkName, spec.NetworkMetadata]:

    return config_read.get_config()['networks']


def get_providers() -> dict[spec.NetworkName, spec.Provider]:
    return config_read.get_config()['providers']


def has_provider(
    *, name=typing.Optional[str], network=typing.Optional[str]
) -> bool:
    try:
        get_provider(name=name, network=network)
        return True
    except LookupError:
        return False


def get_provider(
    *,
    name: typing.Optional[str] = None,
    network: typing.Optional[str] = None,
    protocol: typing.Optional[str] = None,
) -> spec.Provider:

    providers = list(get_providers().values())

    # build query
    query = {}
    if name is None and network is None:
        raise Exception('specify network name or network')
    if name is not None:
        query['name'] = name
    if network is not None:
        query['network'] = network
    if protocol is not None:
        query['protocol'] = protocol

    return search_utils.get_matching_entry(sequence=providers, query=query)


def get_default_network() -> spec.NetworkName:
    return config_read.get_config()['network_defaults']['default_network']


def get_default_provider(
    network: typing.Optional[spec.NetworkName] = None,
) -> spec.Provider:

    if network is None:
        network = get_default_network()

    config = config_read.get_config()
    default_providers = config['network_defaults']['default_providers']

    if network in default_providers:
        provider_name = default_providers[network]
        return get_provider(name=provider_name)
    else:
        raise Exception(
            'no default provider specified for network ' + str(network)
        )

