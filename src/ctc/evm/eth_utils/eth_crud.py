import requests
import web3

from ctc.toolbox import web3_utils
from .. import block_utils


def fetch_eth_total_supply():
    url = 'http://api.etherscan.io/api?module=stats&action=ethsupply'
    response = requests.request(method='get', url=url)
    result_str = response.json()['result']
    return int(result_str)


@block_utils.parallelize_block_fetching()
def fetch_eth_balance(
    address, normalize=True, web3_instance=None, provider=None, block=None
):
    if block is None:
        block = 'latest'
    if web3_instance is None:
        web3_instance = web3_utils.create_web3_instance(provider=provider)

    address = web3.Web3.toChecksumAddress(address)
    balance = web3_instance.eth.getBalance(address, block)

    if normalize:
        balance = balance / 1e18

    return balance

