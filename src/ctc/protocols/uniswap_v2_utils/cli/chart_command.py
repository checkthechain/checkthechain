from __future__ import annotations

import asyncio
import functools
import os
import math

import rich.console
import toolstr
import tooltime

from ctc import evm
from ctc import rpc
from ctc.toolbox.defi_utils import ohlc_utils
from ctc.protocols import uniswap_v2_utils


def get_command_spec():
    return {
        'f': async_chart_command,
        'args': [
            {
                'name': 'pool',
            },
            {
                'name': '--inverse',
                'action': 'store_true',
            }
        ],
    }


async def async_chart_command(pool, inverse):
    import numpy as np

    metadata_task = asyncio.create_task(
        uniswap_v2_utils.async_get_pool_tokens_metadata(pool)
    )

    n_candles = math.floor((os.get_terminal_size().columns - 10) / 2)
    candle_timescale = '1d'
    candle_seconds = tooltime.timelength_to_seconds(candle_timescale)
    window_seconds = candle_seconds * n_candles

    window_end = tooltime.create_timestamp()
    window_start = (
        math.floor((window_end - window_seconds) / candle_seconds)
        * candle_seconds
    )
    start_block = await evm.async_get_block_of_timestamp(window_start) - 1
    end_block = await evm.async_get_latest_block_number()

    # get data
    swaps = await uniswap_v2_utils.async_get_pool_swaps(
        pool,
        start_block=start_block,
        end_block=end_block,
    )

    # compute candlesticks
    prices = np.nan_to_num(swaps['x_sold'] / swaps['y_bought']) + np.nan_to_num(
        swaps['x_bought'] / swaps['y_sold']
    )
    if inverse:
        prices = 1 / prices
    block_timestamps = await evm.async_get_blocks_timestamps(
        swaps.index.get_level_values('block_number')
    )
    ohlc = ohlc_utils.compute_ohlc(
        values=prices,
        indices=block_timestamps,
        bin_size=candle_seconds,
    )
    ohlc = ohlc.iloc[-n_candles:]

    min_price = min(prices)
    max_price = max(prices)
    min_time = ohlc.index[0]
    max_time = ohlc.index[-1] + candle_seconds
    render_grid = toolstr.create_grid(
        n_rows=20,
        n_columns=n_candles * 2,
        xmin=min_time - 0.05 * (max_time - min_time),
        xmax=max_time + 0.05 * (max_time - min_time),
        ymin=min_price - 0.05 * (max_price - min_price),
        ymax=max_price + 0.05 * (max_price - min_price),
    )
    sample_grid = toolstr.create_grid(sample_mode='quadrants', **render_grid)
    result = toolstr.raster_candlesticks(ohlc.values, sample_grid, render_grid)
    raster = result['raster']
    color_grid = result['color_grid']

    as_str = toolstr.render_supergrid(
        raster,
        sample_mode='quadrants',
        color_grid=color_grid,
        color_map=toolstr.candlestick_color_map,
    )

    console = rich.console.Console(theme=rich.theme.Theme(inherit=False))

    y_axis = toolstr.render_y_axis(
        grid=render_grid,
    )
    y_axis_width = len(y_axis.split('\n')[0])
    graph = toolstr.concatenate_blocks([y_axis, as_str])

    formatter = functools.partial(
        toolstr.format_timestamp,
        representation='TimestampDate',
    )
    x_axis = toolstr.render_x_axis(
        grid=render_grid,
        formatter=formatter,
    )
    x_axis = toolstr.indent_block(x_axis, indent=y_axis_width)

    metadata = await metadata_task

    toolstr.print_text_box(metadata['x_symbol'] + '-' + metadata['y_symbol'] + ' Uniswap V2 Pool')
    print('each candle =', candle_timescale)
    # print('- n_candlesticks:', n_candles)
    print()
    console.print(graph)
    console.print(x_axis)

    await rpc.async_close_http_session()

