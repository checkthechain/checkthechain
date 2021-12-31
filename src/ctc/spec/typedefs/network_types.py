import typing


NetworkId = int
NetworkName = str
NetworkReference = typing.Union[NetworkId, NetworkName, None]


class NetworkMetadata(typing.TypedDict):
    name: NetworkName
    chain_id: int
    block_explorer: str  # url

