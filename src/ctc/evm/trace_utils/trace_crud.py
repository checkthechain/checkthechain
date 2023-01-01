from __future__ import annotations

from ctc import spec


async def async_get_transaction_trace(
    transaction_hash: spec.TransactionHash,
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

