from ctc import spec
from . import config_utils


def get_data_root() -> str:
    return config_utils.get_config()['data_root']


def get_default_network() -> spec.NetworkName:
    return config_utils.get_config()['default_network']


def get_providers() -> dict[spec.NetworkName, spec.ProviderSpec]:
    return config_utils.get_config()['providers']


def get_custom_networks() -> dict[spec.NetworkName, spec.NetworkMetadata]:
    return config_utils.get_config()['custom_networks']

