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
    *, name=typing.Optional[str], network=typing.Optional[str]
) -> spec.Provider:

    providers = list(get_providers().values())

    # build query
    query = {}
    if name is None and network is None:
        raise Exception('specify network name or network_id')
    if name is not None:
        query['name'] = name
    if network is None:
        query['network_id'] = network

    return search_utils.get_matching_entry(sequence=providers, **query)


def get_default_network() -> spec.NetworkName:
    return config_read.get_config()['network_defaults']['default_network']


def get_default_provider(network: spec.NetworkName) -> spec.Provider:
    defaults = config_read.get_config()['network_defaults']['default_providers']
    if network not in defaults:
        raise Exception(
            'no default provider specified for network ' + str(network)
        )
    else:
        return get_provider(name=defaults[network])

