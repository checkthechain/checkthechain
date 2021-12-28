import typing

from . import rpc_types


NetworkId = int
NetworkName = str
NetworkReference = typing.Union[NetworkId, NetworkName, None]


class NetworkMetadata(typing.TypedDict):
    name: NetworkName
    network_id: int
    block_explorer: str  # url


class NetworkSettings(NetworkMetadata):
    default_provider: rpc_types.ProviderName

