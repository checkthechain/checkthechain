from ctc import directory
from ctc import evm
from . import chainlink_fetch


async def async_fetch_eth_price(**kwargs):
    defaults = {'block': None, 'format': 'answer', 'normalize': True}
    kwargs = dict(defaults, **kwargs)
    usd_per_eth = await chainlink_fetch.async_fetch_feed_datum('ETH_USD', **kwargs)
    return usd_per_eth


async def async_find_feed_first_block(
    feed, start_search=None, end_search=None, verbose=True
):
    if not evm.is_address_str(feed):
        feed = directory.get_oracle_address(name=feed, protocol='chainlink')
    return evm.async_get_contract_creation_block(
        contract_address=feed,
        start_block=start_search,
        end_block=end_search,
        verbose=verbose,
    )

