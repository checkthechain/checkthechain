from __future__ import annotations

import typing

from ctc import spec


async def async_get_block_trace(
    block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> spec.TraceList:
    """get list of call traces for block"""
    from ctc import rpc

    result: spec.TraceList = await rpc.async_trace_block(
        block,
        context=context,
    )
    return result


async def async_get_blocks_trace(
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.TraceList]:
    """get list of call traces for block"""
    import asyncio
    from ctc import rpc
    coroutines = [
        rpc.async_trace_block(block, context=context)
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)


async def async_get_transaction_trace(
    transaction_hash: spec.TransactionHash,
    *,
    context: spec.Context = None,
) -> spec.TraceList:
    """get list of call traces for transaction"""
    from ctc import rpc

    result: spec.TraceList = await rpc.async_trace_transaction(
        transaction_hash,
        context=context,
    )
    return result


async def async_get_transaction_state_diff(
    transaction_hash: spec.TransactionHash,
    *,
    context: spec.Context = None,
) -> spec.StateDiffTrace:
    """get state diff trace for transaction"""
    from ctc import rpc

    result: spec.TraceReplayResult = await rpc.async_trace_replay_transaction(
        transaction_hash,
        trace_type=['stateDiff'],
        context=context,
    )
    state_diff = result['state_diff']
    if state_diff is None:
        raise Exception('stateDiff could not be obtained')
    else:
        return state_diff


async def async_get_transaction_vm_trace(
    transaction_hash: spec.TransactionHash,
    *,
    context: spec.Context = None,
) -> spec.VMTrace:
    """get vm trace for transaction"""
    from ctc import rpc

    result: spec.TraceReplayResult = await rpc.async_trace_replay_transaction(
        transaction_hash,
        trace_type=['vmTrace'],
        context=context,
    )
    vm_trace = result['vm_trace']
    if vm_trace is None:
        raise Exception('vmTrace could not be obtained')
    else:
        return vm_trace

