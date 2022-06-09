from __future__ import annotations

import time

import tooltime
import toolstr

from ctc import rpc
from ctc.protocols import chainlink_utils
from . import chainlink_feed_metadata
from . import chainlink_spec


async def async_summarize_feed(feed: str, n_recent: int = 20) -> None:

    import asyncio

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
        age = tooltime.timelength_to_phrase(time.time() - timestamp)
        age = ' '.join(age.split(' ')[:2]).strip(',')
        update = [
            row['answer'],
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
    toolstr.print_text_box(title, double=False)
    print('- name:', name)
    print('- address:', feed_address)
    print('- aggregator:', aggregator)
    print('- decimals:', decimals)
    # print('- deviation threshold:')
    # print('- heartbeat:')
    print()
    print()
    toolstr.print_header('Recent Updates')
    print()
    labels = ['value', 'age', 'block', 'timestamp', 'time']

    toolstr.print_table(
        updates[-n_recent:][::-1],
        labels=labels,
        indent='    ',
        column_format={'value': {'decimals': 5}},
    )
