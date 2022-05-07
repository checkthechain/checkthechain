from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from .. import connect_utils
from .. import db_crud
from .. import db_management


T = typing.TypeVar('T', int, spec.Block)


async def async_is_block_fully_confirmed(block: int | spec.Block, network) -> bool:

    if isinstance(block, int):
        block_number = block
    else:
        block_number = block['number']

    # check whether block is older than newest block in db
    max_db_block = _get_max_block_number(network=network)
    if block_number < max_db_block:
        return True

    # check whether block has enough confirmations
    provider: spec.ProviderSpec = {'network': network}
    rpc_latest_block = await rpc.async_eth_block_number(provider=provider)
    required_confirmations = db_management.get_required_confirmations(
        network=network,
    )
    return block_number <= rpc_latest_block - required_confirmations


async def async_filter_fully_confirmed_blocks(
    blocks: typing.Sequence[T], network
) -> typing.Sequence[T]:

    block_numbers = []
    for block in blocks:
        if isinstance(block, dict):
            block_numbers.append(block['number'])
        elif isinstance(block, int):
            block_numbers.append(block)
        else:
            raise Exception('unknown block format')

    # check whether all blocks older than newest block in db
    max_block_number = max(block_numbers)
    max_db_block = _get_max_block_number(network=network)
    if max_db_block > max_block_number:
        return blocks

    # check whether blocks have enough confirmations
    provider: spec.ProviderSpec = {'network': network}
    rpc_latest_block = await rpc.async_eth_block_number(provider=provider)
    required_confirmations = db_management.get_required_confirmations(
        network=network,
    )
    max_allowed_block = rpc_latest_block - required_confirmations
    return [
        block
        for block, block_number in zip(blocks, block_numbers)
        if block_number <= max_allowed_block
    ]


def _get_max_block_number(network):
    engine = connect_utils.create_engine(
        datatype='block_timestamps',
        network=network,
    )
    if engine is None:
        raise Exception('could not connect to database')
    with engine.begin() as conn:
        return db_crud.get_max_block_number(network=network, conn=conn)
