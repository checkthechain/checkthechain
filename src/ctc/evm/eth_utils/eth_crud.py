import requests

from .. import address_utils
from .. import block_utils
from .. import rpc_utils


def fetch_eth_total_supply():
    url = 'http://api.etherscan.io/api?module=stats&action=ethsupply'
    response = requests.request(method='get', url=url)
    result_str = response.json()['result']
    return int(result_str)


@block_utils.parallelize_block_fetching()
def fetch_eth_balance(address, normalize=True, provider=None, block=None):
    if block is None:
        block = 'latest'

    address = address_utils.get_address_checksum(address)
    balance = rpc_utils.eth_get_balance(address=address, block=block)

    if normalize:
        balance = balance / 1e18

    return balance

