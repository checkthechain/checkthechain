from __future__ import annotations

import typing

from .. import binary_utils
from ctc import spec


def encode_block_number(block: spec.BlockNumberReference) -> str:
    """encode block number as hex str"""

    standard_block = standardize_block_number(block)

    if isinstance(standard_block, str):
        return standard_block
    elif isinstance(standard_block, int):
        return binary_utils.binary_convert(
            standard_block,
            'prefix_hex',
            keep_leading_0=False,
        )
    else:
        raise Exception('could not encode block number')


#
# # singular block standardization
#


def standardize_block_number(
    block: typing.Optional[spec.BlockNumberReference],
) -> spec.StandardBlockNumber:
    """turn block into standard block number reference

    Examples of standard block numbers: 'latest' or 123456
    """

    if block is None:
        block = 'latest'

    if block in spec.block_number_names:
        if typing.TYPE_CHECKING:
            return typing.cast(spec.BlockNumberName, block)
        else:
            return block
    else:
        return raw_block_number_to_int(block)


def raw_block_number_to_int(block: spec.RawBlockNumber) -> int:
    """convert block number to int"""

    # python3.7 compatibility
    # supports_int = isinstance(block, typing.SupportsInt)
    supports_int = hasattr(block, '__int__')

    if supports_int:
        if isinstance(block, int):
            return block
        else:
            block_supports_int = typing.cast(typing.SupportsInt, block)
            as_int = int(round(block_supports_int))  # type: ignore
            if abs(as_int - int(block_supports_int)) > 0.0001:
                raise Exception('must specify integer blocks')
            return as_int
    elif isinstance(block, str):
        if block.startswith('0x'):
            try:
                return int(block, 16)
            except ValueError:
                pass
        elif 'e' in block:
            as_float = float(block)
            as_int = int(as_float)
            if abs(as_float - as_int) > 0.0001:
                raise Exception('must specify integer blocks')
            else:
                return as_int
        else:
            return int(block)

    raise Exception('unknown block number specification: ' + str(block))


#
# # plural block standardization
#


def standardize_block_numbers(
    blocks: typing.Iterable[spec.BlockNumberReference],
) -> list[spec.StandardBlockNumber]:
    """standardize an iterable of block number references"""
    return [standardize_block_number(block) for block in blocks]


def raw_block_numbers_to_ints(
    blocks: typing.Iterable[spec.RawBlockNumber],
) -> list[int]:
    """convert block numbers to integer"""
    return [raw_block_number_to_int(block) for block in blocks]
