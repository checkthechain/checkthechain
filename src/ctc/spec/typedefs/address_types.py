import typing


Address = str
ContractAddress = str
TokenAddress = ContractAddress
TokenSymbol = str
TokenReference = typing.Union[TokenAddress, TokenSymbol]


class AddressRequiredMetadata(typing.TypedDict):
    name: str  # human readable name
    address: Address  # 20 byte address data


class AddressMetadata(AddressRequiredMetadata, total=False):
    first_block: typing.Optional[int]  # the block this address started existing
    contract_name: typing.Optional[str]  # name as appears in verified contract
    label: str  # protocol name, project name, etc


Oracletype = typing.Literal['feed', 'amm']


class OracleFeedMetadata(AddressMetadata, total=True):
    numerator: typing.Optional[str]
    denominator: typing.Optional[str]
    deviation: float  # percentage
    heartbeat: int  # number of seconds
    decimals: int


class TokenMetadata(AddressMetadata):
    symbol: str
    decimals: str

