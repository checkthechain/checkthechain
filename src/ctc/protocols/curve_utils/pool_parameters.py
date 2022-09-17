from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from . import curve_spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_pool_A(
    pool: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> int:

    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['A'],
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_future_A_time(
    pool: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['future_A_time'],
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_initial_A(
    pool: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['initial_A'],
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_initial_A_time(
    pool: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['initial_A_time'],
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_future_A(
    pool: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['future_A'],
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_ramps() -> spec.DataFrame:
    """get Ramp events"""
    raise NotImplementedError()


async def async_get_A_history(
    pool: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[float]:
    """get history of pool's A parameter"""

    import asyncio
    import numpy as np
    from ctc.toolbox import pd_utils

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        provider=provider,
    )

    # get ramp events
    pool_start_block = await evm.async_get_contract_creation_block(
        pool,
        verbose=False,
        provider=provider,
    )
    latest_block = await evm.async_get_latest_block_number(provider=provider)
    blocks: spec.NumpyArray = np.arange(start_block, end_block, dtype=int)
    block_timestamps_task = asyncio.create_task(
        evm.async_get_block_timestamps(
            blocks=typing.cast(typing.Sequence[int], blocks),
            provider=provider,
        )
    )

    event_abi: spec.EventABI = {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'name': 'old_A',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'name': 'new_A',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'name': 'initial_time',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'name': 'future_time',
                'type': 'uint256',
            },
        ],
        'name': 'RampA',
        'type': 'event',
    }

    events = await evm.async_get_events(
        contract_address=pool,
        event_abi=event_abi,
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
    block_timestamps = await block_timestamps_task

    # need per-block timestamps over a long time range to continue :-\
    A = compute_A(
        initial_A=typing.cast(
            typing.Sequence[typing.Union[int, float]], events['arg__old_A']
        ),
        future_A=typing.cast(
            typing.Sequence[typing.Union[int, float]], events['arg__new_A']
        ),
        initial_A_time=typing.cast(
            typing.Sequence[typing.Union[int, float]],
            events['arg__initial_time'],
        ),
        future_A_time=typing.cast(
            typing.Sequence[typing.Union[int, float]],
            events['arg__future_time'],
        ),
        timestamps=block_timestamps,
    )

    return A


def compute_A(
    *,
    initial_A: typing.Sequence[int | float],
    initial_A_time: typing.Sequence[int | float],
    future_A: typing.Sequence[int | float],
    future_A_time: typing.Sequence[int | float],
    timestamps: typing.Sequence[int | float],
) -> typing.Sequence[float]:
    """perform linear interpolation between initial and future A values

    TODO: need to convert to int?
    """

    import numpy as np

    result = _compute_A(
        initial_A=np.array(initial_A),
        initial_A_time=np.array(initial_A_time),
        future_A=np.array(future_A),
        future_A_time=np.array(future_A_time),
        timestamps=np.array(timestamps),
    )

    return list(result)


def _compute_A(
    *,
    initial_A: spec.NumpyArray,
    initial_A_time: spec.NumpyArray,
    future_A: spec.NumpyArray,
    future_A_time: spec.NumpyArray,
    timestamps: spec.NumpyArray,
) -> spec.NumpyArray:

    intercept = initial_A
    slope = (future_A - initial_A) / (future_A_time - initial_A_time)
    result = intercept + slope * (timestamps - initial_A_time)

    mask = timestamps > future_A_time
    result[mask] = future_A

    if typing.TYPE_CHECKING:
        return typing.cast(spec.NumpyArray, result)
    else:
        return result
