from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

import tooltime

from ctc import evm
from ctc import spec
from . import twap_data
from . import twap_filter


class DataSource(TypedDict, total=False):
    protocol: typing.Literal['UniswapV2', 'Chainlink']
    feed: [str, spec.Address]
    composite_feed: [str, spec.Address]
    invert: bool
    normalize: bool
    mode: typing.Literal['native', 'raw']


async def async_get_twap(
    data_source: DataSource,
    #
    # # data samples
    filter_duration: tooltime.Timestamp,
    #
    # # output samples
    output_start_time: typing.Union[str, int],
    output_start_block: typing.Union[str, int],
    output_end_block: typing.Union[str, int],
    output_end_time: typing.Union[str, int],
    output_sample_rate: None,
    provider: spec.ProtocolSpec,
) -> spec.Series:

    # get block numbers and timestamps
    start_coroutine = evm.async_get_block_number_and_time(
        block_number=output_start_block,
        block_timestamp=output_start_time,
        provider=provider,
    )
    start_task = asyncio.create_task(start_coroutine)
    end_coroutine = evm.async_get_block_number_and_time(
        block_number=output_end_block,
        block_timestamp=output_end_time,
        provider=provider,
    )
    end_task = asyncio.create_task(end_coroutine)
    start_block, start_time = await start_task
    end_block, end_time = await end_task

    # start block timestamp acquisition task
    blocks = list(range(start_block, end_block + 1))
    block_timestamps_task = asyncio.create_task(
        evm.async_get_blocks_timestamps(blocks=blocks, provider=provider)
    )

    # get data
    data = await twap_data.async_get_data_feed(
        data_source=data_source,
        start_block=start_block,
        end_block=end_block,
    )

    # filter data if necessary
    mode = data_source.get('mode')
    if mode == 'native':
        twap = data
    elif mode == 'raw':
        twap = twap_filter.filter_twap(
            raw_values=data.values,
            timestamps=(await block_timestamps_task),
            filter_duration=filter_duration,
        )
    else:
        raise Exception('unknown mode: ' + str(mode))

    return twap


async def async_get_twap_single_sample(
    data_source,
    block=None,
    timestamp=None,
    protocol=None,
) -> float:

    series = await async_get_twap(
        data_source=data_source,
        start_block=block,
        end_block=block,
        start_time=timestamp,
        end_time=timestamp,
        protocol=protocol,
    )

    if len(series) == 0:
        raise Exception()
    elif len(series) > 1:
        raise Exception()
    else:
        return series.values[0]

