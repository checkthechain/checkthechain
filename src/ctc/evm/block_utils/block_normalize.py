from __future__ import annotations

import asyncio
import typing

from ctc import spec
from . import block_crud


#
# # conversions
#


async def async_block_number_to_int(
    block: spec.BlockNumberReference,
    provider: spec.ProviderSpec = None,
) -> int:
    """resolve block number reference to int (e.g. converting 'latest' to int)

    Examples: 'latest', or 9999.0, or 9999
    """
    if block in spec.block_number_names:
        return await block_crud.async_get_latest_block_number(provider=provider)
    else:
        return raw_block_number_to_int(block)


def standardize_block_number(
    block: spec.BlockNumberReference,
) -> spec.StandardBlockNumber:
    """turn block into standard block number reference

    Examples: 'latest' or 123456
    """

    if block in spec.block_number_names:
        return typing.cast(spec.BlockNumberName, block)
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
# # plural versions
#


async def async_block_numbers_to_int(
    blocks: typing.Iterable[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
) -> list[int]:
    coroutines = [
        async_block_number_to_int(block=block, provider=provider)
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)


def standardize_block_numbers(
    blocks: typing.Iterable[spec.BlockNumberReference],
) -> list[spec.StandardBlockNumber]:
    """standardize an iterable of block number references"""
    return [standardize_block_number(block) for block in blocks]


def raw_block_number_to_ints(
    blocks: typing.Iterable[spec.RawBlockNumber],
) -> list[int]:
    return [raw_block_number_to_int(block) for block in blocks]

