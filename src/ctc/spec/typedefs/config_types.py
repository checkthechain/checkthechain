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

from . import network_types
from . import rpc_types
import typing


class ConfigNetworkDefaults(typing.TypedDict):
    default_network: network_types.NetworkName
    default_providers: dict[network_types.NetworkName, rpc_types.ProviderName]


class PartialConfigSpec(typing.TypedDict, total=False):
    version: str
    data_dir: str
    providers: dict[rpc_types.ProviderName, rpc_types.Provider]
    networks: dict[network_types.NetworkName, network_types.NetworkMetadata]
    network_defaults: ConfigNetworkDefaults


class ConfigSpec(typing.TypedDict):
    version: str
    data_dir: str
    providers: dict[rpc_types.ProviderName, rpc_types.Provider]
    networks: dict[network_types.NetworkName, network_types.NetworkMetadata]
    network_defaults: ConfigNetworkDefaults

