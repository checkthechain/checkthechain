"""

## Config Keys
- version: version of config schema
- data_dir: root directory for storing ctc data
- default_network: default network to use when none specified
- providers: default provider for each network
- networks: custom user-defined networks


## TODO
- add additional config settings
    - rpc: set batching and other parameters for each rpc method
    - sql: configuration for sql database backend
"""

import typing
from typing_extensions import TypedDict

from . import network_types
from . import rpc_types


class ConfigNetworkDefaults(TypedDict):
    default_network: network_types.NetworkName
    default_providers: typing.Dict[
        network_types.NetworkName, rpc_types.ProviderName
    ]


class PartialConfigSpec(TypedDict, total=False):
    config_spec_version: str
    data_dir: str
    providers: typing.Dict[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Dict[
        network_types.NetworkName, network_types.NetworkMetadata
    ]
    network_defaults: ConfigNetworkDefaults


class ConfigSpec(TypedDict):
    config_spec_version: str
    data_dir: str
    providers: typing.Dict[rpc_types.ProviderName, rpc_types.Provider]
    networks: typing.Dict[
        network_types.NetworkName, network_types.NetworkMetadata
    ]
    network_defaults: ConfigNetworkDefaults

