from __future__ import annotations

import typing

from ctc import spec


async def async_trace_contract_creations(
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> typing.Sequence[typing.Any]:

    import asyncio
    import ctc.rpc
    from ctc.rpc.rpc_decoders import create_trace_decoder

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
        dict(trace, block_number=block_number)  # type: ignore
        for block_number, subresult in zip(blocks, result)
        for trace in create_trace_decoder.decode_create_traces(subresult)
    ]

    return create_traces


async def async_trace_native_transfers(
    start_block: spec.BlockNumberReference,
    end_block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> typing.Sequence[typing.Any]:

    # extract block replays from server
    import asyncio
    import ctc.rpc
    from ctc.rpc.rpc_decoders import native_transfer_decoder

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

