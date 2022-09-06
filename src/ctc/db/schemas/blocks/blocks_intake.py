from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from ... import management
from ... import connect_utils
from ... import intake_utils
from . import blocks_statements
from ..block_timestamps import block_timestamps_statements
from ..block_gas import block_gas_statements
from .. import block_gas

if typing.TYPE_CHECKING:
    import toolsql


#
# # singular
#


async def async_intake_block(
    block: spec.Block,
    network: spec.NetworkReference,
) -> None:
    """intake block and extract relevant information to db tables

    under normal operation should store raw block or block timestamp, noth both
    """

    # check whether to intake
    active_schemas = management.get_active_schemas()
    intake_block_object = active_schemas.get('blocks')
    intake_block_timestamp = active_schemas.get('block_timestamps')
    intake_block_gas = active_schemas.get('block_gas')

    # check that block is confirmed
    if intake_block_object or intake_block_timestamp:
        if not await intake_utils.async_is_block_fully_confirmed(
            block=block, network=network
        ):
            intake_block_object = False
            intake_block_timestamp = False

    # insert into databases
    if intake_block_object or intake_block_timestamp or intake_block_gas:
        engine = connect_utils.create_engine(
            schema_name='block_timestamps',
            network=network,
        )
        if engine is None:
            return

        with engine.begin() as conn:
            # do not perform these concurrently to prevent deadlocks
            await _async_intake_block_object(
                block=block,
                conn=conn,
                network=network,
            )
            await _async_intake_block_timestamp(
                block=block,
                conn=conn,
                network=network,
            )
            await _async_intake_block_gas(
                block=block,
                conn=conn,
                network=network,
            )


async def _async_intake_block_object(
    block: spec.Block,
    *,
    network: spec.NetworkReference,
    conn: toolsql.SAConnection,
) -> None:

    await blocks_statements.async_upsert_block(
        block=block,
        conn=conn,
        network=network,
    )


async def _async_intake_block_timestamp(
    block: spec.Block | None,
    *,
    network: spec.NetworkReference,
    conn: toolsql.SAConnection,
    block_number: int | None = None,
    timestamp: int | None = None,
) -> None:

    # get block_number and timestamp
    if block_number is None or timestamp is None:
        if block is None:
            raise Exception('must specify block or block_number and timestamp')
        block_number = block['number']
        timestamp = block['timestamp']

    # store in db
    await block_timestamps_statements.async_upsert_block_timestamp(
        conn=conn,
        block_number=block_number,
        timestamp=timestamp,
        network=network,
    )


async def _async_intake_block_gas(
    block: spec.Block,
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    if len(block['transactions']) == 0 or isinstance(
        block['transactions'][0], dict
    ):
        await block_gas_statements.async_upsert_median_block_gas_fee(
            block_number=block['number'],
            median_gas_fee=evm.compute_median_block_gas_fee(
                block,
                normalize=False,
            ),
            timestamp=block['timestamp'],
            conn=conn,
            network=network,
        )


#
# # plural
#


async def async_intake_blocks(
    blocks: typing.Sequence[spec.Block],
    network: spec.NetworkReference,
    *,
    latest_block_number: int | None = None,
) -> None:

    if len(blocks) == 0:
        return

    # check whether schemas are active
    active_schemas = management.get_active_schemas()
    intake_block_objects = active_schemas.get('blocks')
    intake_block_timestamps = active_schemas.get('block_timestamps')
    intake_block_gases = active_schemas.get('block_gas')

    # check which blocks are confirmed
    confirmed_blocks = await intake_utils.async_filter_fully_confirmed_blocks(
        blocks=blocks,
        network=network,
        latest_block_number=latest_block_number,
    )

    if intake_block_objects or intake_block_timestamps or intake_block_gases:
        engine = connect_utils.create_engine(
            schema_name='block_timestamps',
            network=network,
        )
        if engine is None:
            return

        with engine.begin() as conn:
            # do not perform these concurrently to prevent deadlocks
            await _async_intake_block_objects(
                confirmed_blocks=confirmed_blocks,
                network=network,
                conn=conn,
            )
            await _async_intake_block_timestamps(
                confirmed_blocks=confirmed_blocks,
                network=network,
                conn=conn,
            )
            await _async_intake_blocks_gas(
                blocks=blocks,
                conn=conn,
                network=network,
            )


async def _async_intake_block_objects(
    confirmed_blocks: typing.Sequence[spec.Block],
    *,
    network: spec.NetworkReference,
    conn: toolsql.SAConnection,
) -> None:

    if len(confirmed_blocks) > 0:
        await blocks_statements.async_upsert_blocks(
            conn=conn,
            blocks=confirmed_blocks,
            network=network,
        )


async def _async_intake_block_timestamps(
    confirmed_blocks: typing.Sequence[spec.Block] | None = None,
    *,
    confirmed_block_timestamps: typing.Mapping[int, int] | None = None,
    network: spec.NetworkReference,
    conn: toolsql.SAConnection,
) -> None:

    if confirmed_blocks is not None and confirmed_block_timestamps is not None:
        raise Exception('cannot specify both blocks and block_timestamps')

    # determine timestamps
    if confirmed_blocks is not None:
        confirmed_block_timestamps = {
            block['number']: block['timestamp'] for block in confirmed_blocks
        }
    else:
        raise Exception('specify either blocks or block_timestamps')

    # store in database
    if len(confirmed_block_timestamps) > 0:
        await block_timestamps_statements.async_upsert_block_timestamps(
            conn=conn,
            block_timestamps=confirmed_block_timestamps,
        )


async def _async_intake_blocks_gas(
    blocks: typing.Sequence[spec.Block],
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    # only perform on blocks that have full transactions included
    blocks_gas_data: typing.MutableSequence[block_gas.BlockGasRow] = []
    for block in blocks:
        if len(block['transactions']) == 0 or isinstance(
            block['transactions'][0], dict
        ):
            fee = evm.compute_median_block_gas_fee(
                block,
                normalize=False,
            )
            block_gas_data: block_gas.BlockGasRow = {
                'block_number': block['number'],
                'timestamp': block['timestamp'],
                'median_gas_fee': fee,
            }
            blocks_gas_data.append(block_gas_data)

    # insert into db
    if len(blocks_gas_data) > 0:
        await block_gas_statements.async_upsert_median_blocks_gas_fees(
            block_gas_data=blocks_gas_data,
            conn=conn,
            network=network,
        )
