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

    data = chainlink_utils.get_feed_data(
        feed_address=feed_address,
        answer_only=False,
        verbose=False,
    )
    most_recent = data.iloc[-1]
    timestamp = most_recent['arg__updatedAt']
    block_number, _, _ = data.index[-1]

    updates = []
    for i, row in data.iterrows():
        timestamp = row['arg__updatedAt']
        age = tooltime.timelength_to_phrase(time.time() - timestamp)
        age = ' '.join(age.split(' ')[:2]).strip(',')
        update = [
            toolstr.format(row['arg__current'] / (10 ** decimals), decimals=3),
            age,
            str(i[0]),
            str(timestamp),
            tooltime.timestamp_to_iso(timestamp).replace('T', ' '),
        ]
        updates.append(update)

    title = 'Chainlink Feed: ' + name
    toolstr.print_header(title, double=False)
    print('- name:', name)
    print('- address:', feed_address)
    print('- aggregator:', aggregator)
    print('- decimals:', decimals)
    # print('- deviation threshold:')
    # print('- heartbeat:')
    print()
    print()
    print('Recent Updates:')
    print()
    headers = ['value', 'age', 'block', 'timestamp', 'time']
    table = tooltable.print_table(updates[-n_recent:][::-1], headers=headers)

