import typing


Address = str
ContractAddress = str
TokenAddress = ContractAddress
TokenSymbol = str
TokenReference = typing.Union[TokenAddress, TokenSymbol]


# class AddressDataset(typing.TypedDict):
#     name: str  # name of dataset
#     network_id: int  # int id of network


class AddressRequiredMetadata(typing.TypedDict):
    name: str  # human readable name
    address: Address  # 20 byte address data


class AddressMetadata(AddressRequiredMetadata, total=False):
    block: int  # the block this address started existing
    contract_name: str  # name as appears in verified contract
    protocol: str  # protocol associated with address


class OracleFeedMetadata(AddressMetadata, total=True):
    deviation: float  # percentage
    heartbeat: int  # number of seconds
    decimals: int


class TokenMetadata(typing.TypedDict):
    symbol: str
    decimals: str

