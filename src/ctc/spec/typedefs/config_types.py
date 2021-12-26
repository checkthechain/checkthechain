"""

## Config Keys
- data_root: root directory for storing ctc data
- defeault_network: default network to use when none specified
- providers: default provider for each network
- custom_networks: custom user-defined networks


## TODO
- add additional config settings
    - rpc: set batching and other parameters for each rpc method
    - sql: configuration for sql database backend
"""

from . import network_types
from . import rpc_types
import typing


config_path_env_var = 'CTC_CONFIG_PATH'


class PartialConfigSpec(typing.TypedDict, total=False):
    data_root: str
    default_network: network_types.NetworkName
    providers: dict[network_types.NetworkName, rpc_types.ProviderSpec]
    custom_networks: dict[
        network_types.NetworkName, network_types.NetworkMetadata
    ]


class ConfigSpec(typing.TypedDict):
    data_root: str
    default_network: network_types.NetworkName
    providers: dict[network_types.NetworkName, rpc_types.ProviderSpec]
    custom_networks: dict[
        network_types.NetworkName, network_types.NetworkMetadata
    ]

