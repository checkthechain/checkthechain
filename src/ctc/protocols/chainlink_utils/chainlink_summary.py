from __future__ import annotations

import time

import tooltime
import toolstr

from ctc import evm
from ctc import rpc
from ctc.cli import cli_run
from ctc.protocols import chainlink_utils
from . import chainlink_feed_metadata
from . import chainlink_spec


async def async_summarize_feed(
    feed: str,
    *,
    n_recent: int = 20,
    verbose: bool = False,
) -> None:

    import asyncio

    styles = cli_run.get_cli_styles()

    feed_address = await chainlink_feed_metadata.async_resolve_feed_address(
        feed,
    )

    name_coroutine = rpc.async_eth_call(
        function_abi=chainlink_spec.feed_function_abis['description'],
        to_address=feed_address,
    )
    decimals_coroutine = rpc.async_eth_call(
        function_abi=chainlink_spec.feed_function_abis['decimals'],
        to_address=feed_address,
    )
    aggregator_coroutine = rpc.async_eth_call(
        function_abi=chainlink_spec.feed_function_abis['aggregator'],
        to_address=feed_address,
    )
    name_task = asyncio.create_task(name_coroutine)
    decimals_task = asyncio.create_task(decimals_coroutine)
    aggregator_task = asyncio.create_task(aggregator_coroutine)

    latest_block = await rpc.async_eth_block_number()
    data = await chainlink_utils.async_get_feed_data(
        feed_address,
        fields='full',
        start_block=latest_block - 5000,
    )
    most_recent = data.iloc[-1]
    timestamp = most_recent['timestamp']

    updates = []
    for i, row in data.iterrows():
        timestamp = int(row['timestamp'])
        age = tooltime.timelength_to_phrase(int(time.time() - timestamp))
        age = ' '.join(age.split(' ')[:2]).strip(',')
        update = [
            toolstr.format(row['answer'], decimals=4, trailing_zeros=True),
            age,
            str(i),
            str(timestamp),
            tooltime.timestamp_to_iso(timestamp).replace('T', ' '),
        ]
        updates.append(update)

    name = await name_task
    decimals = await decimals_task
    aggregator = await aggregator_task

    title = 'Chainlink Feed Summary: ' + name
    toolstr.print_text_box(title, double=False, style=styles['title'])
    toolstr.print(
        toolstr.add_style('- name:', styles['option']),
        toolstr.add_style(name, styles['description']),
    )
    toolstr.print(
        toolstr.add_style('- decimals:', styles['option']),
        toolstr.add_style(str(decimals), styles['description']),
    )

    metadata = await chainlink_feed_metadata.async_get_feed_metadata(feed)
    deviation = toolstr.format(
        float(metadata['deviation']) / 100,
        percentage=True,
    )
    toolstr.print(
        toolstr.add_style('- deviation threshold:', styles['option']),
        toolstr.add_style(deviation, styles['description']),
    )
    toolstr.print(
        toolstr.add_style('- heartbeat:', styles['option']),
        toolstr.add_style(metadata['heartbeat'], styles['description']),
    )
    toolstr.print(
        toolstr.add_style('- address:', styles['option']),
        toolstr.add_style(feed_address, styles['metavar']),
    )
    toolstr.print(
        toolstr.add_style('- aggregator:', styles['option']),
        toolstr.add_style(aggregator, styles['metavar']),
    )

    creation_block = await chainlink_feed_metadata.async_get_feed_first_block(
        feed
    )
    creation_timestamp = await evm.async_get_block_timestamp(creation_block)
    toolstr.print(
        toolstr.add_style('- feed creation block:', styles['option']),
        toolstr.add_style(str(creation_block), styles['description']),
    )
    toolstr.print(
        toolstr.add_style('- feed creation timestamp:', styles['option']),
        toolstr.add_style(str(creation_timestamp), styles['description']),
    )
    toolstr.print(
        toolstr.add_style('- feed age:', styles['option']),
        toolstr.add_style(
            tooltime.get_age(creation_timestamp, 'TimelengthPhrase'),
            styles['description'],
        ),
    )

    if verbose:
        print()
        print('fetching aggregator history...')
        history = await chainlink_utils.async_get_feed_aggregator_history(
            feed_address,
            provider=None,
        )
        print()
        toolstr.print_header('Aggregator History', style=styles['title'])
        history_blocks = sorted(history.values())
        raw_timestamps = await evm.async_get_block_timestamps(history_blocks)
        history_timestamps = dict(zip(history.keys(), raw_timestamps))
        history_rows = []
        for old_aggregator, block in history.items():
            age_seconds: str = tooltime.get_age(
                history_timestamps[old_aggregator],
                'TimelengthPhrase',
            )
            age = ' '.join(age_seconds.split(' ')[:2]).strip(',')
            history_row = [
                old_aggregator,
                str(block),
                age,
            ]
            history_rows.append(history_row)
        labels = ['address', 'block', 'age']
        toolstr.print_table(
            history_rows,
            labels=labels,
            indent='    ',
            label_style=styles['title'],
            column_styles={'address': styles['metavar']},
            border=styles['comment'],
        )

    print()
    print()
    toolstr.print_header('Recent Updates', style=styles['title'])
    print()
    labels = ['value', 'age', 'block', 'timestamp', 'time']

    toolstr.print_table(
        updates[-n_recent:][::-1],
        labels=labels,
        indent='    ',
        column_formats={'value': {'decimals': 5}},
        column_styles={
            'value': styles['description'] + ' bold',
        },
        label_style=styles['title'],
        border=styles['comment'],
    )

    xvals = data['timestamp'].values.astype(float)
    yvals = data['answer'].values.astype(float)
    plot = toolstr.render_line_plot(
        xvals=xvals,  # type: ignore
        yvals=yvals,  # type: ignore
        n_rows=40,
        n_columns=120,
        line_style=styles['description'],
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
        xaxis_kwargs={'tick_label_format': 'age'},
    )
    print()
    print()
    print()
    toolstr.print(
        toolstr.hjustify(name + ' feed over time', 'center', 70),
        indent=4,
        style=styles['title'],
    )
    toolstr.print(plot, indent=4)
