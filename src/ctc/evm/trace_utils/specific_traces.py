from __future__ import annotations

import typing

from ctc import spec
from .. import block_utils


async def async_trace_contract_creations(
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> typing.Sequence[typing.Any]:
    """collect contract creation traces"""
    import asyncio
    import ctc.rpc
    from ctc.rpc.rpc_decoders import create_trace_decoder

    start_block, end_block = await block_utils.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        to_int=True,
        allow_none=False,
        context=context,
    )

    blocks = list(range(start_block, end_block + 1))

    coroutines = [
        ctc.rpc.async_trace_block(
            block,
            decode_response=False,
            snake_case_response=False,
            raw_output=True,
            context=context,
        )
        for block in blocks
    ]
    result = await asyncio.gather(*coroutines)

    create_traces: typing.Sequence[typing.Any] = [
        trace
        for block_number, subresult in zip(blocks, result)
        for trace in create_trace_decoder.decode_create_traces(
            subresult, block_number=block_number
        )
    ]

    return create_traces


async def async_trace_native_transfers(
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> typing.Sequence[typing.Any]:
    """collect native transfer traces"""
    # extract block replays from server
    import asyncio
    import ctc.rpc
    from ctc.rpc.rpc_decoders import native_transfer_decoder

    start_block, end_block = await block_utils.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        to_int=True,
        allow_none=False,
        context=context,
    )

    block_numbers = list(range(start_block, end_block + 1))
    coroutines = [
        ctc.rpc.async_trace_replay_block_transactions(
            block,
            trace_type=['trace'],
            decode_response=False,
            snake_case_response=False,
            raw_output=True,
            context=context,
        )
        for block in block_numbers
    ]
    responses = await asyncio.gather(*coroutines)

    native_transfers = native_transfer_decoder.decode_native_transfers(
        responses=responses, block_numbers=block_numbers
    )

    return native_transfers


async def async_trace_slot_stats(
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> spec.DataFrame:
    """collect slot stat traces"""
    # extract block replays from server
    import asyncio
    import polars as pl
    import ctc.rpc
    from ctc.rpc.rpc_decoders import slot_diff_decoder

    start_block, end_block = await block_utils.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        to_int=True,
        allow_none=False,
        context=context,
    )

    block_numbers = list(range(start_block, end_block + 1))
    coroutines = [
        ctc.rpc.async_trace_replay_block_transactions(
            block,
            trace_type=['stateDiff'],
            decode_response=False,
            snake_case_response=False,
            raw_output=True,
            context=context,
        )
        for block in block_numbers
    ]
    responses = await asyncio.gather(*coroutines)

    # parse into slots data
    slot_data = slot_diff_decoder.decode_slot_stats(
        raw_responses=responses,
        block_numbers=block_numbers,
    )
    flat_slot_data = slot_diff_decoder.flatten_slots_data(slot_data)

    # convert to dataframe
    columns = [
        ('contract_address', pl.datatypes.Utf8),
        ('slot', pl.datatypes.Utf8),
        ('value', pl.datatypes.Utf8),
        ('first_nonzero_block', pl.datatypes.Int32),
        ('last_zero_block', pl.datatypes.Int32),
        ('last_updated_block', pl.datatypes.Int32),
        ('n_tx_updates', pl.datatypes.Int32),
    ]
    df = pl.DataFrame(flat_slot_data, schema=columns)

    return df

