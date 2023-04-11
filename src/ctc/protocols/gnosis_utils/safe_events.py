from __future__ import annotations

import ast
import typing

from ctc import evm
from ctc import spec
from . import safe_spec


async def async_get_safe_setup(
    safe_address: spec.Address,
    *,
    context: spec.Context = None,
) -> typing.Mapping[str, typing.Any] | None:
    creation_block = await evm.async_get_contract_creation_block(safe_address, context=context)
    events = await evm.async_get_events(
        safe_address,
        event_abi=safe_spec.event_abis['SafeSetup'],
        verbose=False,
        start_block=creation_block,
        end_block=creation_block,
        context=context,
    )
    if len(events) == 0:
        return None
    setup = events[:1].to_dicts()[0]
    setup['arg__owners'] = ast.literal_eval(setup['arg__owners'])
    return setup


async def async_get_safe_executions(
    safe_address: spec.Address,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    return await evm.async_get_events(
        safe_address,
        event_abi=safe_spec.event_abis['ExecutionSuccess'],
        start_block=start_block,
        end_block=end_block,
        verbose=False,
        context=context,
    )


async def async_get_safe_owner_adds(
    safe_address: spec.Address,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    return await evm.async_get_events(
        safe_address,
        event_abi=safe_spec.event_abis['AddedOwner'],
        start_block=start_block,
        end_block=end_block,
        verbose=False,
        context=context,
    )


async def async_get_safe_owner_removes(
    safe_address: spec.Address,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    return await evm.async_get_events(
        safe_address,
        event_abi=safe_spec.event_abis['RemovedOwner'],
        start_block=start_block,
        end_block=end_block,
        verbose=False,
        context=context,
    )


async def async_get_safe_threshold_changes(
    safe_address: spec.Address,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    return await evm.async_get_events(
        safe_address,
        event_abi=safe_spec.event_abis['ChangedThreshold'],
        start_block=start_block,
        end_block=end_block,
        verbose=False,
        context=context,
    )


async def async_get_safe_guard_changes(
    safe_address: spec.Address,
    *,
    context: spec.Context = None,
) -> spec.DataFrame:
    return await evm.async_get_events(
        safe_address,
        event_abi=safe_spec.event_abis['ChangedGuard'],
        verbose=False,
        context=context,
    )

