import eth_abi
import numpy as np
import web3

from fei.data import web3_utils
from . import chainlink_fetch


def fetch_eth_price(**kwargs):
    defaults = {'block': None, 'format': 'answer', 'normalize': True}
    kwargs = dict(defaults, **kwargs)
    usd_per_eth = chainlink_fetch.fetch_feed_datum('ETH_USD', **kwargs)
    return usd_per_eth


def find_feed_first_block(
    feed, start_search=None, end_search=None, verbose=True, condition='nonzero'
):
    if start_search is None:
        start_search = 0
    if end_search is None:
        end_search = web3_utils.fetch_latest_block_number()

    kwargs = {
        'feed': feed,
        'results': {},
        'verbose': verbose,
        'condition': condition,
    }

    if _is_feed_started(block=start_search, **kwargs):
        raise Exception('feed might start before start_search')
    if not _is_feed_started(block=end_search, **kwargs):
        raise Exception('feed might end after end_search')

    while True:
        midpoint = (start_search + end_search) / 2
        midpoint = int(midpoint)

        if _is_feed_started(block=midpoint, **kwargs):
            end_search = midpoint
        else:
            start_search = midpoint

        if start_search + 1 == end_search:
            return end_search
        elif _is_feed_started(block=start_search, **kwargs):
            return start_search
        elif not _is_feed_started(block=end_search, **kwargs):
            return end_search + 1


def _is_feed_started(feed, block, results, verbose, condition):

    if block not in results:

        try:
            datum = chainlink_fetch.fetch_feed_datum(feed, block=block)

            if condition == 'exists':
                results[block] = True
            elif condition == 'nonzero':
                results[block] = not np.isclose(datum['answer'], 0)
            else:
                raise Exception('unknown condition: ' + str(condition))

        except (
            eth_abi.exceptions.InsufficientDataBytes,
            web3.exceptions.BadFunctionCallOutput,
            ValueError,
        ):
            results[block] = False

        if verbose:
            print(
                'queried block='
                + str(block)
                + ', active='
                + str(results[block])
            )

    return results[block]

