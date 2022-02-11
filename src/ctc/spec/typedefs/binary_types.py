import typing
from typing_extensions import Literal


BinaryData = typing.Union[bytes, str]
BinaryInteger = typing.Union[int, BinaryData]
BlockSpec = typing.Union[
    int, BinaryData, Literal['latest', 'earliest', 'pending']
]

BinaryFormat = Literal['binary', 'prefix_hex', 'raw_hex', 'integer']

IntegerData = int

PrefixHexData = str
RawHexData = str
HexData = typing.Union[PrefixHexData, RawHexData]

Data = typing.Union[IntegerData, BinaryData, HexData]

