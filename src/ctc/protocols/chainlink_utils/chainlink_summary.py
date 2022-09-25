from __future__ import annotations

import time

import tooltime
import toolstr

from ctc import cli
from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.protocols import chainlink_utils
from . import chainlink_feed_metadata
from . import chainlink_spec


async def async_print_feed_summary(
    feed: str,
    *,
    start_block: spec.BlockNumberReference | None = None,
    n_recent: int | None = None,
    verbose: bool = False,
) -> None:

    import asyncio

    styles = cli.get_cli_styles()

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

    if start_block is None:
        if n_recent is None:
            n_recent = 20
        latest_block = await rpc.async_eth_block_number()
        start_block = latest_block - 6000 * n_recent
    else:
        n_recent = 999999999999
    data = await chainlink_utils.async_get_feed_data(
        feed_address,
        fields='full',
        start_block=start_block,
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
    cli.print_bullet(key='name', value=name)
    cli.print_bullet(key='decimals', value=str(decimals))

    metadata = await chainlink_feed_metadata.async_get_feed_metadata(feed)
    deviation = toolstr.format(
        float(metadata['deviation']) / 100,
        percentage=True,
    )
    cli.print_bullet(key='deviation threshold', value=deviation)
    cli.print_bullet(key='heartbeat', value=metadata['heartbeat'])
    cli.print_bullet(key='address', value=feed_address)
    cli.print_bullet(key='aggregator', value=aggregator)

    creation_block = await chainlink_feed_metadata.async_get_feed_first_block(
        feed
    )
    creation_timestamp = await evm.async_get_block_timestamp(creation_block)
    cli.print_bullet(key='feed creation block', value=str(creation_block))
    cli.print_bullet(
        key='feed creation timestamp',
        value=str(creation_timestamp),
    )
    cli.print_bullet(
        key='feed age',
        value=tooltime.get_age(creation_timestamp, 'TimelengthPhrase'),
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
        label_style=styles['title'],
        border=styles['comment'],
        limit_rows=21,
        column_styles={
            'value': styles['description'] + ' bold',
            'age': styles['description'],
            'block': styles['option'],
            'timestamp': styles['option'],
            'time': styles['option'],
        },
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
