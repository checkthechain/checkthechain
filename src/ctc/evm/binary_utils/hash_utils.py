import typing
from typing import Literal, Optional

import sha3

from ctc import spec
from . import format_utils


@typing.overload
def keccak(data: spec.BinaryInteger, output_format: Literal['integer']) -> int:
    ...


@typing.overload
def keccak(data: spec.BinaryInteger, output_format: Literal['binary']) -> bytes:
    ...


@typing.overload
def keccak(
    data: spec.BinaryInteger,
    output_format: Literal['prefix_hex', 'raw_hex', None],
) -> str:
    ...


def keccak(
    data: spec.BinaryInteger,
    output_format: Optional[spec.BinaryFormat] = 'prefix_hex',
) -> spec.BinaryInteger:
    """return keccack-256 hash of hex or binary data"""
    data = format_utils.convert_binary_format(data, 'binary')
    binary = sha3.keccak_256(data).digest()
    return format_utils.convert_binary_format(binary, output_format)


@typing.overload
def keccak_text(text: str, output_format: Literal['integer']) -> int:
    ...


@typing.overload
def keccak_text(text: str, output_format: Literal['binary']) -> bytes:
    ...


@typing.overload
def keccak_text(
    text: str, output_format: Literal['prefix_hex', 'raw_hex', None]
) -> str:
    ...


def keccak_text(
    text: str, output_format: Optional[spec.BinaryFormat] = 'prefix_hex'
) -> spec.BinaryInteger:
    """return keccack-256 hash of text"""
    return keccak(text.encode(), output_format)

