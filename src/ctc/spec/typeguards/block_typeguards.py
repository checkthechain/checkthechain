from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard

from ctc import binary
from ..typedefs import block_types
from . import binary_typeguards


def is_block_number_name(
    block: typing.Any,
) -> TypeGuard[block_types.BlockNumberName]:
    return block in block_types.block_number_names


def is_raw_block_number(
    block: typing.Any,
) -> TypeGuard[block_types.RawBlockNumber]:

    # python3.7 compatibility
    # supports_int = isinstance(block, typing.SupportsInt)
    supports_int = hasattr(block, '__int__')

    return supports_int or binary_typeguards.is_hex_data(block)


def is_standard_block_number(
    block: typing.Any,
) -> TypeGuard[block_types.StandardBlockNumber]:
    return isinstance(block, int) or is_block_number_name(block)


def is_block_number_reference(
    block: typing.Any,
) -> TypeGuard[block_types.BlockNumberReference]:
    return is_raw_block_number(block) or is_standard_block_number(block)


def is_block_hash(block: typing.Any) -> TypeGuard[block_types.BlockHash]:
    return (
        binary_typeguards.is_hex_data(block)
        and binary.get_binary_n_bytes(block) == 32
    )


def is_block_reference(
    block: typing.Any,
) -> TypeGuard[block_types.BlockReference]:
    return is_block_number_reference(block) or is_block_hash(block)

