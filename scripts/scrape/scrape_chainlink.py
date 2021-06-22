#!/usr/bin/env python3

from fei.data.protocols import chainlink_data


save_feeds = [
    'ETH_USD',
    'FEI_ETH',
]

print('scraping chainlink feeds:')
for feed in save_feeds:
    print('-', feed)
print()


for feed in save_feeds:
    print('saving feed:', feed)
    print()
    chainlink_data.save_feed_to_present(feed=feed)
    print()
    print()

print()
print()
print('done')

