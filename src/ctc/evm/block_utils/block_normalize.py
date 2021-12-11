import asyncio
import typing

from ctc import spec
from . import block_search
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
    """turn block into standard block reference

    Examples: 'latest' or 123456
    """

    if block in spec.block_number_names:
        return block
    else:
        return raw_block_number_to_int(block)


def raw_block_number_to_int(block: spec.RawBlockNumber) -> int:
    """convert block number to int"""
    if isinstance(block, typing.SupportsInt):
        if not isinstance(block, int):
            as_int = int(round(block))
            if abs(as_int - block) > 0.0001:
                raise Exception('must specify integer blocks')
            block = as_int
        return block
    elif isinstance(block, str):
        try:
            return int(block, 16)
        except ValueError:
            pass

    raise Exception('unknown block number specification: ' + str(block))


#
# # plural versions
#


async def async_block_numbers_to_int(
    blocks: typing.Iterable[spec.BlockNumberReference],
    provider: spec.ProviderSpec,
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


#
# # old functions
#


def normalize_block(block, contract_address=None):
    if block is None:
        raise Exception()

    if block == 'latest':
        block = block_crud.get_block_number('latest')
    if block == 'contract_start':
        block = block_search.get_contract_creation_block(
            contract_address=contract_address
        )

    return int(block)


def normalize_blocks(blocks, contract_address=None):
    kwargs = {'contract_address': contract_address}

    special = {}
    for block in blocks:
        if block in ['latest', 'earliest', 'pending'] and block not in special:
            special[block] = normalize_block(block, **kwargs)

    normalized = []
    for block in blocks:
        if block in special:
            normalized.append(special[block])
        else:
            normalized.append(normalize_block(block, **kwargs))

    return normalized


def normalize_block_range(start_block, end_block, contract_address=None):
    """fill in special values and defaults for block range

    - must fill in dynamic 'latest' values when using a range in multiple calls
    """

    # fill in default values
    if start_block is None:
        if contract_address is not None:
            start_block = 'contract_start'
        else:
            start_block = 'latest'
    if end_block is None:
        end_block = 'latest'

    # fill in special values
    if 'contract_start' in [start_block, end_block]:
        contract_start = block_search.get_contract_creation_block(
            contract_address=contract_address
        )
    if 'latest' in [start_block, end_block]:
        latest_block = block_crud.get_block_number('latest')

    # assign special values
    if start_block == 'latest':
        start_block = latest_block
    if start_block == 'contract_start':
        start_block = contract_start
    if end_block == 'latest':
        end_block = latest_block
    if end_block == 'contract_start':
        end_block = contract_start

    # convert to int
    start_block = int(start_block)
    end_block = int(end_block)

    return (start_block, end_block)

