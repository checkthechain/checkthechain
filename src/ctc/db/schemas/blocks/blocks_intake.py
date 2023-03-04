from __future__ import annotations

import typing

from ctc import config
from ctc import evm
from ctc import spec

from ... import management
from ... import intake_utils
from ..block_timestamps import block_timestamps_statements
from ..transactions import transactions_intake
from . import blocks_statements

if typing.TYPE_CHECKING:
    import toolsql


async def async_intake_block(
    *,
    db_block: spec.DBBlock | None = None,
    rpc_block: spec.RPCBlock | None = None,
    context: spec.Context,
) -> None:

    if rpc_block is not None and db_block is not None:
        raise Exception('cannot specify rpc_block and db_block')
    elif rpc_block is not None:
        await async_intake_blocks(rpc_blocks=[rpc_block], context=context)
    elif db_block is not None:
        await async_intake_blocks(db_blocks=[db_block], context=context)
    else:
        raise Exception('must specify rpc_block or db_block')


async def async_intake_blocks(
    *,
    db_blocks: typing.Sequence[spec.DBBlock] | None = None,
    rpc_blocks: typing.Sequence[spec.RPCBlock] | None = None,
    latest_block_number: int | None = None,
    blocks_db_transactions: typing.Sequence[spec.DBTransaction] | None = None,
    context: spec.Context,
) -> None:
    """intake block and extract relevant information to db tables

    under normal operation should store raw block or block timestamp, noth both
    """

    import toolsql

    # check whether to intake
    active_schemas = management.get_active_schemas()
    intake_blocks = active_schemas.get('blocks')
    intake_transactions = active_schemas.get('transactions')
    intake_block_timestamps = active_schemas.get('block_timestamps')

    # get db blocks
    if rpc_blocks is not None and db_blocks is not None:
        raise Exception('should specify only rpc_blocks or db_blocks')
    if db_blocks is None:
        if rpc_blocks is None:
            raise Exception('must specify rpc_blocks or db_blocks')
        db_blocks = [
            evm.convert_rpc_block_to_db_block(rpc_block)
            for rpc_block in rpc_blocks
        ]

    if len(db_blocks) == 0:
        return

    # filter unconfirmed blocks
    db_config = config.get_context_db_config(
        schema_name='blocks',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        filtered_db_blocks = (
            await intake_utils.async_filter_fully_confirmed_blocks(
                db_blocks,
                context=context,
                latest_block_number=latest_block_number,
                conn=conn,
            )
        )
    if len(filtered_db_blocks) == 0:
        return
    db_blocks = filtered_db_blocks
    block_numbers = [block['number'] for block in db_blocks]

    # get db_block_transactions
    if (
        intake_transactions
        and blocks_db_transactions is None
        and rpc_blocks is not None
    ):
        import asyncio

        blocks_rpc_transactions: typing.Sequence[spec.RPCTransaction] = [
            tx  # type: ignore
            for rpc_block in rpc_blocks
            for tx in rpc_block['transactions']
            if rpc_block['number'] in block_numbers
            and len(rpc_block['transactions']) > 0
            and isinstance(rpc_block['transactions'][0], dict)
        ]
        coroutines = [
            evm.async_convert_rpc_transaction_to_db_transaction(
                transaction=tx, context=context
            )
            for tx in blocks_rpc_transactions
        ]
        blocks_db_transactions = await asyncio.gather(*coroutines)

    # insert into database
    if intake_blocks or intake_transactions:
        # do not perform these inserts concurrently to prevent deadlocks
        db_config = config.get_context_db_config(
            schema_name='blocks',
            context=context,
        )
        async with toolsql.async_connect(db_config) as conn:
            if intake_blocks:
                await blocks_statements.async_upsert_blocks(
                    blocks=db_blocks,
                    conn=conn,
                    context=context,
                )
            if intake_block_timestamps:
                await _async_intake_blocks_timestamps(
                    confirmed_blocks=db_blocks,
                    context=context,
                    conn=conn,
                )
        if blocks_db_transactions is not None and intake_transactions:
            await transactions_intake.async_intake_blocks_transactions(
                block_numbers=block_numbers,
                transactions=blocks_db_transactions,
                context=context,
            )


async def _async_intake_blocks_timestamps(
    confirmed_blocks: typing.Sequence[spec.DBBlock] | None = None,
    *,
    confirmed_block_timestamps: typing.Mapping[int, int] | None = None,
    context: spec.Context,
    conn: toolsql.AsyncConnection,
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
            context=context,
        )


#
# # singular
#


# async def async_intake_block(
#     *,
#     db_block: spec.DBBlock | None = None,
#     rpc_block: spec.RPCBlock | None = None,
#     context: spec.Context,
# ) -> None:
#     """intake block and extract relevant information to db tables

#     under normal operation should store raw block or block timestamp, noth both
#     """

#     if rpc_block is not None and db_block is not None:
#         raise Exception('should specify only rpc_block or db_block')
#     if db_block is None:
#         if rpc_block is None:
#             raise Exception('must specify rpc_block or db_block')
#         else:
#             db_block = evm.block_utils.block_crud._rpc_block_to_db_block(
#                 rpc_block
#             )
#             transactions = rpc_block['transactions']
#     else:
#         transactions = None

#     # check whether to intake
#     active_schemas = management.get_active_schemas()
#     intake_block_object = active_schemas.get('blocks')
#     intake_transactions = active_schemas.get('transactions')

#     # check that block is confirmed
#     if not await intake_utils.async_is_block_fully_confirmed(
#         block=db_block['number'], context=context
#     ):
#         return

#     # insert into databases
#     if intake_block_object or intake_transactions:
#         engine = connect_utils.create_engine(
#             schema_name='block_timestamps',
#             context=context,
#         )
#         if engine is None:
#             return

#         with engine.begin() as conn:
#             # do not perform these concurrently to prevent deadlocks
#             await blocks_statements.async_upsert_block(
#                 block=db_block,
#                 conn=conn,
#                 context=context,
#             )
#             if transactions is not None and active_schemas.get('transactions'):
#                 transactions = [
#                     tx for tx in transactions if isinstance(tx, dict)
#                 ]
#                 if len(transactions) > 0:
#                     await _async_intake_block_transactions(
#                         transactions=transactions,
#                         block_number=db_block['number'],
#                         conn=conn,
#                         context=context,
#                     )


# async def _async_intake_block_timestamp(
#     block: spec.DBBlock | None,
#     *,
#     context: spec.Context,
#     conn: toolsql.SAConnection,
#     block_number: int | None = None,
#     timestamp: int | None = None,
# ) -> None:

#     # get block_number and timestamp
#     if block_number is None or timestamp is None:
#         if block is None:
#             raise Exception('must specify block or block_number and timestamp')
#         block_number = block['number']
#         timestamp = block['timestamp']

#     # store in db
#     await block_timestamps_statements.async_upsert_block_timestamp(
#         conn=conn,
#         block_number=block_number,
#         timestamp=timestamp,
#         context=context,
#     )

#
# # plural
#


# async def async_intake_blocks(
#     blocks: typing.Sequence[spec.DBBlock | spec.RPCBlock],
#     *,
#     context: spec.Context,
#     latest_block_number: int | None = None,
# ) -> None:

#     if len(blocks) == 0:
#         return

#     # check whether schemas are active
#     active_schemas = management.get_active_schemas()
#     intake_block_objects = active_schemas.get('blocks')
#     intake_block_timestamps = active_schemas.get('block_timestamps')
#     intake_block_gases = active_schemas.get('block_gas')

#     # check which blocks are confirmed
#     confirmed_blocks = await intake_utils.async_filter_fully_confirmed_blocks(
#         blocks=blocks,
#         context=context,
#         latest_block_number=latest_block_number,
#     )

#     if len(confirmed_blocks) == 0:
#         return

#     # convert to db blocks
#     db_blocks = [
#         evm.block_utils.block_crud._rpc_block_to_db_block(block)
#         for block in confirmed_blocks
#     ]

#     if intake_block_objects or intake_block_timestamps or intake_block_gases:
#         engine = connect_utils.create_engine(
#             schema_name='block_timestamps',
#             context=context,
#         )
#         if engine is None:
#             return

#         with engine.begin() as conn:
#             # do not perform these concurrently to prevent deadlocks
#             await blocks_statements.async_upsert_blocks(
#                 conn=conn,
#                 blocks=db_blocks,
#                 context=context,
#             )
#             await _async_intake_block_timestamps(
#                 confirmed_blocks=db_blocks,
#                 context=context,
#                 conn=conn,
#             )
#         await async_intake_blocks_transactions(
#             blocks=db_blocks,
#             context=context,
#         )

