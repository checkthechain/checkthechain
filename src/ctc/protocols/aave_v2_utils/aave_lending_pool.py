from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from . import aave_spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_deposits(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    context: spec.Context = None,
) -> spec.DataFrame:

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        context=context,
    )

    if end_block is None:
        end_block = 'latest'

    aave_lending_pool = aave_spec.get_aave_address(
        name='LendingPool',
        context=context,
    )
    events = await evm.async_get_events(
        contract_address=aave_lending_pool,
        event_name='Deposit',
        start_block=start_block,
        end_block=end_block,
        include_timestamps=include_timestamps,
        verbose=False,
        context=context,
    )

    return events


async def async_get_withdrawals(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    context: spec.Context = None,
) -> spec.DataFrame:

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        context=context,
    )

    if end_block is None:
        end_block = 'latest'

    aave_lending_pool = aave_spec.get_aave_address(
        name='LendingPool',
        context=context,
    )
    events = await evm.async_get_events(
        contract_address=aave_lending_pool,
        event_name='Withdraw',
        start_block=start_block,
        include_timestamps=include_timestamps,
        end_block=end_block,
        verbose=False,
        context=context,
    )

    return events
