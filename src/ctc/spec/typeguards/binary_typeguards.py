from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard

from ..typedefs import binary_types


def is_data(data: typing.Any) -> TypeGuard[binary_types.Data]:
    return (
        is_integer_data(data)
        or is_binary_data(data)
        or is_hex_data(data)
    )


def is_integer_data(data: typing.Any) -> TypeGuard[binary_types.IntegerData]:
    return isinstance(data, int)


def is_binary_data(data: typing.Any) -> TypeGuard[binary_types.BinaryData]:
    return isinstance(data, bytes)


def is_prefix_hex_data(
    data: typing.Any,
) -> TypeGuard[binary_types.PrefixHexData]:
    if not isinstance(data, str):
        return False
    if not data.startswith('0x'):
        return False
    try:
        int(data, 16)
        return True
    except ValueError:
        return False


def is_raw_hex_data(data: typing.Any) -> TypeGuard[binary_types.RawHexData]:
    if not isinstance(data, str):
        return False
    if data.startswith('0x'):
        return False
    try:
        int(data, 16)
        return True
    except ValueError:
        return False


def is_hex_data(data: typing.Any) -> TypeGuard[binary_types.HexData]:
    if not isinstance(data, str):
        return False
    try:
        int(data, 16)
        return True
    except ValueError:
        return False

