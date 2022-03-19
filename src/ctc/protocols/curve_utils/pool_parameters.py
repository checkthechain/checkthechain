from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.toolbox import pd_utils


async def async_get_pool_future_A_time(
    pool: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> int:
    return await rpc.async_eth_call(
        to_address=pool,
        function_name='future_A_time',
        block_number=block,
        provider=provider,
    )


async def async_get_pool_initial_A(
    pool: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> int:
    return await rpc.async_eth_call(
        to_address=pool,
        function_name='initial_A',
        block_number=block,
        provider=provider,
    )


async def async_get_pool_initial_A_time(
    pool: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> int:
    return await rpc.async_eth_call(
        to_address=pool,
        function_name='initial_A_time',
        block_number=block,
        provider=provider,
    )


async def async_get_pool_future_A(
    pool: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> int:
    return await rpc.async_eth_call(
        to_address=pool,
        function_name='future_A',
        block_number=block,
        provider=provider,
    )


async def async_get_pool_ramps():
    raise NotImplementedError()


async def async_get_A_history(
    pool: spec.Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
):
    """get history of pool's A parameter"""

    import numpy as np

    # get ramp events
    pool_start_block = await evm.async_get_contract_creation_block(
        pool,
        verbose=False,
        provider=provider,
    )
    latest_block = await evm.async_get_latest_block_number(provider=provider)
    blocks: spec.NumpyArray = np.arange(start_block, end_block, dtype=int)
    blocks_timestamps_task = asyncio.create_task(
        evm.async_get_blocks_timestamps(
            blocks=typing.cast(typing.Sequence, blocks),
            provider=provider,
        )
    )
    events = await evm.async_get_events(
        contract_address=pool,
        event_name='RampA',
        start_block=pool_start_block,
        end_block=latest_block,
    )
    events = events[
        ['arg__old_A', 'arg__new_A', 'arg__initial_time', 'arg__future_time']
    ]

    # initial deployment parameters
    initial_A = await async_get_pool_initial_A(pool, block=pool_start_block)
    initial_A_time = 0
    events.loc[start_block, 0, 0] = [initial_A, initial_A, initial_A_time, 0]
    events = events.sort_index()

    # interpolate per block
    events = pd_utils.interpolate_dataframe(
        events,
        end_index=latest_block,
        level='block_number',
    )

    # get blocks timestamps
    blocks_timestamps = await blocks_timestamps_task

    # need per-block timestamps over a long time range to continue :-\
    A = compute_A(
        initial_A=typing.cast(typing.Sequence, events['arg__old_A']),
        future_A=typing.cast(typing.Sequence, events['arg__new_A']),
        initial_A_time=typing.cast(
            typing.Sequence,
            events['arg__initial_time'],
        ),
        future_A_time=typing.cast(typing.Sequence, events['arg__future_time']),
        timestamps=blocks_timestamps,
    )

    return A


def compute_A(
    initial_A: typing.Sequence,
    initial_A_time: typing.Sequence,
    future_A: typing.Sequence,
    future_A_time: typing.Sequence,
    timestamps: typing.Sequence,
) -> typing.Sequence[float]:
    """perform linear interpolation between initial and future A values

    TODO: need to convert to int?
    """

    import numpy as np

    return _compute_A(
        initial_A=np.array(initial_A),
        initial_A_time=np.array(initial_A_time),
        future_A=np.array(future_A),
        future_A_time=np.array(future_A_time),
        timestamps=np.array(timestamps),
    )


def _compute_A(
    initial_A: spec.NumpyArray,
    initial_A_time: spec.NumpyArray,
    future_A: spec.NumpyArray,
    future_A_time: spec.NumpyArray,
    timestamps: spec.NumpyArray,
):

    intercept = initial_A
    slope = (future_A - initial_A) / (future_A_time - initial_A_time)
    result = intercept + slope * (timestamps - initial_A_time)

    mask = timestamps > future_A_time
    result[mask] = future_A

    return result

