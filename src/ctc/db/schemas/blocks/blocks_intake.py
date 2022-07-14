from __future__ import annotations

import asyncio
import typing

from ctc import spec

from ... import management
from ... import connect_utils
from ... import intake_utils
from . import blocks_statements
from ..block_timestamps import block_timestamps_statements


async def async_intake_block(
    block: spec.Block,
    network: spec.NetworkReference,
) -> None:
    """intake block and extract relevant information to db tables

    under normal operation should store raw block or block timestamp, noth both
    """
    block_coroutine = async_intake_raw_block(
        block=block,
        network=network,
    )
    timestamp_coroutine = async_intake_block_timestamp(
        block=block,
        network=network,
    )
    await asyncio.gather(
        block_coroutine,
        timestamp_coroutine,
    )


async def async_intake_raw_block(
    block: spec.Block,
    network: spec.NetworkReference,
) -> None:

    # check whether to intake
    if not management.get_active_schemas().get('blocks'):
        return
    if not await intake_utils.async_is_block_fully_confirmed(
        block=block, network=network
    ):
        return

    # store in db
    engine = connect_utils.create_engine(
        schema_name='block_timestamps',
        network=network,
    )
    if engine is None:
        return
    with engine.begin() as conn:
        await blocks_statements.async_upsert_block(
            conn=conn,
            block=block,
            network=network,
        )


async def async_intake_block_timestamp(
    block: spec.Block | None,
    *,
    block_number: int | None = None,
    timestamp: int | None = None,
    network: spec.NetworkReference,
) -> None:

    if block_number is None or timestamp is None:
        if block is None:
            raise Exception('must specify block or block_number and timestamp')
        block_number = block['number']
        timestamp = block['timestamp']

    # check whether to intake
    if not management.get_active_schemas().get('block_timestamps'):
        return
    if not await intake_utils.async_is_block_fully_confirmed(
        block=block_number, network=network
    ):
        return

    # store in db
    engine = connect_utils.create_engine(
        schema_name='block_timestamps',
        network=network,
    )
    if engine is None:
        return
    with engine.begin() as conn:
        await block_timestamps_statements.async_upsert_block_timestamp(
            conn=conn,
            block_number=block_number,
            timestamp=timestamp,
        )


async def async_intake_blocks(
    blocks: typing.Sequence[spec.Block],
    network: spec.NetworkReference,
) -> None:

    if len(blocks) == 0:
        return

    blocks_coroutine = async_intake_raw_blocks(blocks=blocks, network=network)
    timestamps_coroutine = async_intake_block_timestamps(
        blocks=blocks, network=network
    )
    await asyncio.gather(blocks_coroutine, timestamps_coroutine)


async def async_intake_raw_blocks(
    blocks: typing.Sequence[spec.Block],
    network: spec.NetworkReference,
) -> None:

    if len(blocks) == 0:
        return

    if not management.get_active_schemas().get('blocks'):
        return
    confirmed = await intake_utils.async_filter_fully_confirmed_blocks(
        blocks=blocks,
        network=network,
    )
    if len(confirmed) > 0:
        engine = connect_utils.create_engine(
            schema_name='blocks', network=network
        )
        if engine is None:
            return
        with engine.begin() as conn:
            await blocks_statements.async_upsert_blocks(
                conn=conn,
                blocks=confirmed,
                network=network,
            )


async def async_intake_block_timestamps(
    blocks: typing.Sequence[spec.Block] | None = None,
    *,
    block_timestamps: typing.Mapping[int, int] | None = None,
    network: spec.NetworkReference,
) -> None:

    if blocks is not None and block_timestamps is not None:
        raise Exception('cannot specify both blocks and block_timestamps')

    if not management.get_active_schemas().get('block_timestamps'):
        return

    # determine which blocks have enough confirmations
    if blocks is not None:
        if len(blocks) == 0:
            return
        confirmed_blocks = (
            await intake_utils.async_filter_fully_confirmed_blocks(
                blocks=blocks,
                network=network,
            )
        )
        if len(confirmed_blocks) == 0:
            return
        confirmed_block_timestamps = None
    elif block_timestamps is not None:
        if len(block_timestamps) == 0:
            return
        confirmed_numbers = (
            await intake_utils.async_filter_fully_confirmed_blocks(
                blocks=list(block_timestamps.keys()),
                network=network,
            )
        )
        if len(confirmed_numbers) == 0:
            return
        confirmed_block_timestamps = {
            number: block_timestamps[number] for number in confirmed_numbers
        }
        confirmed_blocks = None
    else:
        raise Exception('specify either blocks or block_timestamps')

    # store in database
    engine = connect_utils.create_engine(
        schema_name='block_timestamps',
        network=network,
    )
    if engine is None:
        return
    with engine.begin() as conn:
        await block_timestamps_statements.async_upsert_block_timestamps(
            conn=conn,
            blocks=confirmed_blocks,
            block_timestamps=confirmed_block_timestamps,
        )


#
# # second draft
#


# async def async_intake_blocks(
#     blocks: typing.Sequence[spec.Block],
#     provider: spec.ProviderReference = None,
# ) -> None:
#     """intake block and extract relevant information to db tables"""

#     active_block_schemas = get_active_schemas('block')
#     if len(active_block_schemas) == 0:
#         return

#     intake_blocks = await async_should_intake_blocks(
#         blocks=blocks, provider=provider
#     )
#     if len(intake_blocks) > 0:
#         with engine.begin() as conn:
#             coroutines = []
#             for schema in active_block_schemas:
#                 if schema == 'blocks':
#                     coroutine = db_statements.async_upsert_blocks(
#                         conn=conn,
#                         blocks=intake_blocks,
#                     )
#                     coroutines.append(coroutine)
#                 elif schema == 'block_timestamps':
#                     coroutine = db_statements.async_upsert_blocks_timestamp(
#                         conn=conn,
#                         blocks=should_upsert_block_timestamps,
#                     )
#                     coroutines.append(coroutine)
#                 elif schema == 'block_gas_stats':
#                     coroutine = db_statements.async_upsert_blocks_gas_stats(
#                         conn=conn,
#                         blocks=should_upsert_blocks_gas_stats,
#                     )
#                     coroutines.append(coroutine)
#                 else:
#                     raise Exception('unknown schema: ' + str(schema))
#             await asyncio.gather(*coroutines)


# async def async_should_intake_raw_block(block, network):

#     # check whether already stored
#     db_statements.does_block_exist()


# async def async_should_intake_blocks(blocks, provider):
#     required_confirmations = management.get_required_confirmations(
#         provider=provider
#     )
#     latest_block = None
#     latest_block = await rpc.async_eth_block_number(provider=provider)

#     intake_blocks = []
#     for block in blocks:
#         pass

#     if block['number'] <= max_block - required_confirmations:
#         return True
#     else:
#         latest_block = await rpc.async_eth_block_number(provider=provider)
#         return block['number'] <= latest_block - min_confirmations


##
## # old
##


# async def async_intake_block(
#    block: spec.Block,
#    provider: spec.ProviderReference = None,
# ) -> None:
#    """intake block and extract relevant information to db tables"""

#    # determine whether to store block
#    network = rpc.get_provider_network(provider=provider)
#    min_confirmations = management.get_min_confirmations(
#        schema='block_timestamps',
#        network=network,
#    )
#    engine = connect_utils.create_engine(
#        schema='block_timestamps',
#        network=network,
#    )
#    if engine is None:
#        return

#    check_if_exists = False
#    with engine.connect() as conn:
#        if (
#            check_if_exists
#            and db_statements.get_block_timestamp(
#                conn=conn, block_number=block['number']
#            )
#            is not None
#        ):
#            store = False
#        else:
#            max_block = db_statements.get_max_block_number(conn=conn, network=network)
#            if block['number'] <= max_block - min_confirmations:
#                store = True
#            else:
#                latest_block = await rpc.async_eth_block_number(
#                    provider=provider,
#                )
#                store = block['number'] <= latest_block - min_confirmations

#    # store data in db
#    if store:
#        with engine.begin() as conn:
#            db_statements.set_block_timestamp(
#                conn=conn,
#                block_number=block['number'],
#                timestamp=block['timestamp'],
#            )


# async def async_intake_blocks(
#    blocks: typing.Sequence[spec.Block],
#    provider: spec.ProviderReference = None,
# ) -> None:
#    """

#    TODO: database should store a max_complete_block number
#    - indicates that ALL blocks below this height are stored
#    - enables not re-storing anything below this height upon intake
#    """

#    # determine whether to store block
#    network = rpc.get_provider_network(provider=provider)
#    min_confirmations = management.get_min_confirmations(
#        schema='block_timestamps',
#        network=network,
#    )
#    engine = connect_utils.create_engine(
#        schema='block_timestamps',
#        network=network,
#    )
#    if engine is None:
#        return

#    with engine.connect() as conn:
#        max_intake_block = max(block['number'] for block in blocks)
#        max_stored_block = db_statements.get_max_block_number(
#            conn=conn, network=network
#        )
#        if max_intake_block <= max_stored_block - min_confirmations:
#            store_blocks = blocks
#        else:
#            latest_block = await rpc.async_eth_block_number(
#                provider=provider,
#            )
#            store_blocks = [
#                block
#                for block in blocks
#                if block['number'] <= latest_block - min_confirmations
#            ]

#    # store data in db
#    if len(store_blocks) > 0:
#        block_timestamps = {
#            block['number']: block['timestamp'] for block in store_blocks
#        }
#        with engine.begin() as conn:
#            db_statements.set_block_timestamps(
#                conn=conn,
#                block_timestamps=block_timestamps,
#            )
