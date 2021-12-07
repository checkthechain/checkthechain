import typing

from ctc.evm import binary_utils
from . import block_spec


def is_block_number_name(
    block: typing.Any,
) -> typing.TypeGuard[block_spec.BlockNumberName]:
    return block in block_spec.block_number_names


def is_raw_block_number(
    block: typing.Any,
) -> typing.TypeGuard[block_spec.RawBlockNumber]:
    return isinstance(
        block, typing.SupportsInt
    ) or binary_utils.is_hex_binary_data(block)


def is_standard_block_number(
    block: typing.Any,
) -> typing.TypeGuard[block_spec.StandardBlockNumber]:
    return isinstance(block, int) or is_block_number_name(block)


def is_block_number_reference(
    block: typing.Any,
) -> typing.TypeGuard[block_spec.BlockNumberReference]:
    return is_raw_block_number(block) or is_standard_block_number(block)


def is_block_hash(block: typing.Any) -> typing.TypeGuard[block_spec.BlockHash]:
    return (
        binary_utils.is_hex_binary_data(block)
        and binary_utils.get_binary_n_bytes(block) == 32
    )


def is_block_reference(
    block: typing.Any,
) -> typing.TypeGuard[block_spec.BlockReference]:
    return is_block_number_reference(block) or is_block_hash(block)

