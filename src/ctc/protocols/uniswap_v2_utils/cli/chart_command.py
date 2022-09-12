from __future__ import annotations

import functools
import math

import rich.console
import toolcli
import toolstr
import tooltime

from ctc import cli
from ctc import evm
from ctc import spec
from ctc.toolbox.defi_utils import ohlc_utils
from ctc.protocols import uniswap_v2_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chart_command,
        'help': 'chart price action of uniswap pools',
        'args': [
            {
                'name': 'pool',
                'help': 'Uniswap pool address',
            },
            {
                'name': '--timescale',
                'help': 'size of candlesticks, e.g. 1h, 1d, or 1w',
            },
            {
                'name': '--invert',
                'action': 'store_true',
                'help': 'use inverse of price',
            },
            {
                'name': '--no-volume',
                'action': 'store_true',
                'help': 'hide volume data',
            },
        ],
        'examples': ['0x9928e4046d7c6513326ccea028cd3e7a91c7590a'],
    }


async def async_chart_command(
    *,
    pool: spec.Address,
    invert: bool,
    timescale: str,
    no_volume: bool,
) -> None:
    import asyncio

    metadata_task = asyncio.create_task(
        uniswap_v2_utils.async_get_pool_tokens_metadata(pool)
    )

    columns = toolcli.get_n_terminal_cols()
    n_candles = math.floor((columns - 10) / 2)
    if timescale is None:
        candle_timescale = '1d'
    else:
        candle_timescale = timescale
    candle_seconds = tooltime.timelength_to_seconds(candle_timescale)
    window_seconds = candle_seconds * n_candles

    window_end = tooltime.create_timestamp_seconds()
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
        normalize=True,
        include_volumes=True,
        include_prices=True,
    )

    # compute candlesticks
    prices = swaps['price__0__per__1'].values
    x_volumes = swaps['volume__0'].values
    if invert:
        prices = 1 / prices
    block_timestamps = await evm.async_get_block_timestamps(
        swaps.index.get_level_values('block_number')
    )
    ohlc = ohlc_utils.compute_ohlc(
        values=prices,  # type: ignore
        indices=block_timestamps,
        bin_size=candle_seconds,
        volumes=x_volumes,  # type: ignore
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
        char_dict='quadrants',
        color_grid=color_grid,
        color_map=toolstr.candlestick_color_map,
    )

    console = rich.console.Console(theme=rich.theme.Theme(inherit=False))

    styles = cli.get_cli_styles()
    plot_styles = {
        'tick_label_style': 'bold',
        'chrome_style': '#888888',
    }

    y_axis = toolstr.render_y_axis(
        grid=render_grid,
        **plot_styles,  # type: ignore
    )
    y_axis_width = rich.text.Text.from_markup(y_axis.split('\n')[0]).cell_len
    graph = toolstr.concatenate_blocks([y_axis, as_str])

    formatter = functools.partial(
        toolstr.format_timestamp,
        representation='TimestampDate',
    )
    x_axis = toolstr.render_x_axis(
        grid=render_grid,
        formatter=formatter,
        **plot_styles,  # type: ignore
    )
    x_axis = toolstr.indent_block(x_axis, indent=y_axis_width)

    # compute volume
    if not no_volume:
        ymax = ohlc['volume'].max() * 1.1
        volume_render_grid = toolstr.create_grid(
            n_rows=5,
            n_columns=n_candles * 2,
            xmin=render_grid['xmin'],
            xmax=render_grid['xmax'],
            ymin=0 - ymax / 9,
            ymax=ymax,
        )
        volume_sample_grid = toolstr.create_grid(
            sample_mode='quadrants',
            **volume_render_grid,
        )
        volume_raster = toolstr.raster_bar_chart(
            values=ohlc['volume'],  # type: ignore
            grid=volume_sample_grid,
            bar_width=1,
            bar_gap=3,
            start_gap=1,
        )
        volume_y_axis = toolstr.render_y_axis(
            grid=volume_render_grid,
            n_ticks=1,
            **plot_styles,  # type: ignore
        )

    # wait for metadata
    metadata = await metadata_task

    # print output
    token0 = metadata['x_symbol']
    token1 = metadata['y_symbol']
    toolstr.print_text_box(
        metadata['x_symbol'] + '-' + metadata['y_symbol'] + ' Uniswap V2 Pool',
        style=styles['title'],
    )
    cli.print_bullet(key='pool address', value=pool)
    cli.print_bullet(key='each candle', value=candle_timescale)
    cli.print_bullet(key='n_candles', value=n_candles)
    if invert:
        cli.print_bullet(key='price units', value=str(token1) + ' per ' + str(token0))
    else:
        cli.print_bullet(key='price units', value=str(token0) + ' per ' + str(token1))
    if not no_volume:
        cli.print_bullet(key='volume units', value=token0)
    print()
    console.print(graph)

    if not no_volume:
        volume_bars_str = toolstr.render_supergrid(
            volume_raster, char_dict='quadrants'
        )
        volume_graph = toolstr.concatenate_blocks(
            [volume_y_axis, volume_bars_str]
        )
        toolstr.print(volume_graph)

    # print x axis
    console.print(x_axis)
