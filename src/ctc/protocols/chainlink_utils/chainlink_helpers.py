from ctc import directory
from ctc import evm
from . import chainlink_fetch


def fetch_eth_price(**kwargs):
    defaults = {'block': None, 'format': 'answer', 'normalize': True}
    kwargs = dict(defaults, **kwargs)
    usd_per_eth = chainlink_fetch.fetch_feed_datum('ETH_USD', **kwargs)
    return usd_per_eth


def find_feed_first_block(
    feed, start_search=None, end_search=None, verbose=True
):
    if feed in directory.chainlink_feeds:
        feed = directory.chainlink_feeds[feed]
    return evm.get_contract_creation_block(
        contract_address=feed,
        start_block=start_search,
        end_block=end_search,
        verbose=verbose,
    )

