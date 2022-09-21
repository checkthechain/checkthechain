from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

from ctc import evm
from ctc import spec


async def async_predict_block_timestamp(
    block: typing.SupportsInt,
    *,
    provider: spec.ProviderReference = None,
    window_size: int = 88295,
) -> int:
    """predict timestamp of future block number"""

    block = int(block)

    latest_block = await evm.async_get_block('latest', provider=provider)
    latest_number = latest_block['number']
    if block == latest_number:
        return latest_block['timestamp']
    elif block < latest_number:
        return await evm.async_get_block_timestamp(block, provider=provider)
    else:
        old_block = await evm.async_get_block(
            latest_number - window_size, provider=provider
        )
        mean_block_time = (
            latest_block['timestamp'] - old_block['timestamp']
        ) / (latest_number - old_block['number'])
        return round(
            latest_block['timestamp']
            + (block - latest_number) * mean_block_time
        )


async def async_predict_block_timestamps(
    blocks: typing.Sequence[typing.SupportsInt],
    *,
    provider: spec.ProviderReference = None,
    window_size: int = 100000,
) -> typing.Sequence[int]:
    """predict timestamps of future block numbers"""

    import asyncio

    int_blocks = [int(block) for block in blocks]

    predictions = {}
    old_block_tasks = {}
    window_task = None
    new_blocks = []

    latest_block = await evm.async_get_block('latest', provider=provider)
    latest_number = latest_block['number']

    for block in int_blocks:
        if block == latest_number:
            predictions[block] = latest_block['timestamp']
        elif block < latest_number:
            coroutine = evm.async_get_block_timestamp(block, provider=provider)
            old_block_tasks[block] = asyncio.create_task(coroutine)
        else:
            if window_task is None:
                window_task = evm.async_get_block(
                    latest_number - window_size, provider=provider
                )
            new_blocks.append(block)

    # process new blocks
    if window_task is not None:
        old_block = await window_task
        mean_block_time = (
            latest_block['timestamp'] - old_block['timestamp']
        ) / (latest_number - old_block['number'])
        for new_block in new_blocks:
            new_timestamp = round(
                latest_block['timestamp']
                + (new_block - latest_number) * mean_block_time
            )
            predictions[new_block] = new_timestamp

    # gather old block tasks
    if len(old_block_tasks) > 0:
        old_block_timestamps = await asyncio.gather(*old_block_tasks.values())
        for block, timestamp in zip(
            old_block_tasks.keys(), old_block_timestamps
        ):
            predictions[block] = timestamp

    return [predictions[block] for block in int_blocks]


async def async_predict_timestamp_block(
    timestamp: tooltime.Timestamp,
    *,
    provider: spec.ProviderReference = None,
    window_size: int = 86400 * 16,
) -> int:
    """predict block number of future timestamp"""

    import tooltime

    timestamp = tooltime.timestamp_to_seconds(timestamp)

    latest_block = await evm.async_get_block('latest', provider=provider)
    latest_timestamp = latest_block['timestamp']

    if timestamp == latest_timestamp:
        return latest_block['number']
    elif timestamp < latest_timestamp:
        return await evm.async_get_block_of_timestamp(
            timestamp, provider=provider
        )
    else:
        old_timestamp = latest_timestamp - window_size
        old_block = await evm.async_get_block_of_timestamp(
            old_timestamp, provider=provider
        )
        mean_blocks_per_time = (latest_block['number'] - old_block) / (
            latest_block['timestamp'] - old_timestamp
        )
        return round(
            latest_block['number']
            + (timestamp - latest_timestamp) * mean_blocks_per_time
        )


async def async_predict_timestamp_blocks(
    timestamps: typing.Sequence[tooltime.Timestamp],
    *,
    provider: spec.ProviderReference = None,
    window_size: int = 86400 * 16,
) -> typing.Sequence[int]:
    """predict timestamps of future block numbers"""

    import asyncio
    import tooltime

    int_timestamps = [
        tooltime.timestamp_to_seconds(timestamp) for timestamp in timestamps
    ]

    latest_block = await evm.async_get_block('latest', provider=provider)
    latest_timestamp = latest_block['timestamp']
    old_timestamp_tasks = {}
    new_timestamps = []
    window_task = None

    predictions: dict[int, int | float] = {}
    for timestamp in int_timestamps:
        if timestamp == latest_timestamp:
            predictions[timestamp] = latest_block['number']
        elif timestamp < latest_timestamp:
            coroutine = evm.async_get_block_of_timestamp(
                timestamp, provider=provider
            )
            old_timestamp_tasks[timestamp] = asyncio.create_task(coroutine)
        else:
            if window_task is None:
                window_timestamp = latest_timestamp - window_size
                window_coroutine = evm.async_get_block_of_timestamp(
                    window_timestamp, provider=provider
                )
                window_task = asyncio.create_task(window_coroutine)
            new_timestamps.append(timestamp)

    if window_task is not None:
        window_block = await window_task
        mean_blocks_per_time = (latest_block['number'] - window_block) / (
            latest_timestamp - window_timestamp
        )
        for timestamp in new_timestamps:
            predictions[timestamp] = latest_block[
                'number'
            ] + mean_blocks_per_time * (timestamp - latest_timestamp)

    if len(old_timestamp_tasks) > 0:
        results = await asyncio.gather(*old_timestamp_tasks.values())
        for timestamp, result in zip(old_timestamp_tasks.keys(), results):
            predictions[timestamp] = result

    return [round(predictions[timestamp]) for timestamp in int_timestamps]
