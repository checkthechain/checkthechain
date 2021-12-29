import os

from ctc import spec
from . import config_read


def get_data_root_directory() -> str:
    data_root_directory = config_read.get_config()['data_root_directory']
    data_root_directory = os.path.expanduser(data_root_directory)
    return data_root_directory


def get_default_network() -> spec.NetworkName:
    return config_read.get_config()['default_network']


def get_providers() -> dict[spec.NetworkName, spec.ProviderSpec]:
    return config_read.get_config()['providers']


def get_networks() -> dict[spec.NetworkName, spec.NetworkMetadata]:
    return config_read.get_config()['networks']

