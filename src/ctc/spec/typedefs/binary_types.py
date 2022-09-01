from __future__ import annotations

import typing
from typing_extensions import Literal, TypedDict
from . import abi_types


BinaryData = typing.Union[bytes, str]
BinaryInteger = typing.Union[int, BinaryData]
# BlockSpec = typing.Union[
#     int, BinaryData, Literal['latest', 'earliest', 'pending']
# ]

BinaryFormat = Literal['binary', 'prefix_hex', 'raw_hex', 'integer']
ExtendedBinaryFormat = typing.Union[BinaryFormat, Literal['ascii']]

IntegerData = int

PrefixHexData = str
RawHexData = str
HexData = typing.Union[PrefixHexData, RawHexData]

Data = typing.Union[IntegerData, BinaryData, HexData]


class Eip712StructType(TypedDict):
    name: str
    fields: typing.Mapping[str, abi_types.ABIDatatypeStr]
