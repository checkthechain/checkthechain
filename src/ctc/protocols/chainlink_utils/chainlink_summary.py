import time

import tooltable  # type: ignore
import tooltime
import toolstr

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc.protocols import chainlink_utils


async def async_summarize_feed(feed, n_recent=10):

    if evm.is_address_str(feed):
        feed_address = feed
    elif isinstance(feed, str):
        feed_address = directory.get_oracle_address(
            name=feed, protocol='chainlink'
        )
    else:
        raise Exception('unknown feed specification: ' + str(feed))

    call_kwargs = {'to_address': feed_address}
    name = await rpc.async_eth_call(function_name='description', **call_kwargs)
    decimals = await rpc.async_eth_call(function_name='decimals', **call_kwargs)
    aggregator = await rpc.async_eth_call(
        function_name='aggregator', **call_kwargs
    )

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
        timestamp = row['timestamp']
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
    headers = ['value', 'age', 'block', 'timestamp', 'time']
    tooltable.print_table(
        updates[-n_recent:][::-1], headers=headers, indent='    '
    )

