from __future__ import annotations

import typing
from typing_extensions import Literal, TypedDict
from . import abi_types


BinaryData = typing.Union[bytes, str]
GenericBinaryData = typing.Union[int, BinaryData]
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


# either a single datum or a triplet of (v, r, s)
Signature = typing.Union[Data, typing.Tuple[Data, Data, Data]]


class Eip712StructType(TypedDict):
    # implement nested structs once mypy#13297 is production ready
    # https://github.com/python/mypy/pull/13297
    name: str
    fields: typing.Mapping[str, abi_types.ABIDatatypeStr]
