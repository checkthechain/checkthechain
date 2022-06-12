from __future__ import annotations

import typing
from typing_extensions import TypedDict, Literal


Address = str
ContractAddress = str
ERC20Address = ContractAddress
ERC20Symbol = str
ERC20Reference = typing.Union[ERC20Address, ERC20Symbol]


class AddressRequiredMetadata(TypedDict):
    name: str  # human readable name
    address: Address  # 20 byte address data


class AddressMetadata(AddressRequiredMetadata, total=False):
    first_block: typing.Optional[int]  # the block this address started existing
    contract_name: typing.Optional[str]  # name as appears in verified contract
    label: str  # protocol name, project name, etc


Oracletype = Literal['feed', 'amm']


class OracleFeedMetadata(AddressMetadata, total=True):
    numerator: typing.Optional[str]
    denominator: typing.Optional[str]
    deviation: float  # percentage
    heartbeat: int  # number of seconds
    decimals: int


class ERC20Metadata(TypedDict):
    symbol: str
    decimals: int
    name: str
    address: str
