from __future__ import annotations

import typing

from ctc import evm
from .. import typedata
from . import binary_typeguards

if typing.TYPE_CHECKING:

    from typing_extensions import TypeGuard

    from ..typedefs import block_types


def is_block_number_name(
    block: typing.Any,
) -> TypeGuard[block_types.BlockNumberName]:
    """return whether input is a block number name"""
    return block in typedata.block_number_names


def is_raw_block_number(
    block: typing.Any,
) -> TypeGuard[block_types.RawBlockNumber]:
    """return whether input is a raw block number"""

    # python3.7 compatibility
    # supports_int = isinstance(block, typing.SupportsInt)
    supports_int = hasattr(block, '__int__')

    return supports_int or binary_typeguards.is_hex_data(block)


def is_standard_block_number(
    block: typing.Any,
) -> TypeGuard[block_types.StandardBlockNumber]:
    """return whether input is a standardized block number"""
    return isinstance(block, int) or is_block_number_name(block)


def is_block_number_reference(
    block: typing.Any,
) -> TypeGuard[block_types.BlockNumberReference]:
    """return whether input refers to a block number"""
    return is_raw_block_number(block) or is_standard_block_number(block)


def is_block_hash(block: typing.Any) -> TypeGuard[block_types.BlockHash]:
    """return whether input is a block hash"""
    return (
        binary_typeguards.is_hex_data(block)
        and evm.get_binary_n_bytes(block) == 32
    )


def is_block_reference(
    block: typing.Any,
) -> TypeGuard[block_types.BlockReference]:
    """return whether input is a block number or block hash"""
    return is_block_number_reference(block) or is_block_hash(block)
