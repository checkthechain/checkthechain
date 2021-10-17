import json

import requests


def get_contract_abi_from_etherscan(contract_address):
    """fetch contract abi using etherscan"""
    url_template = 'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw'
    abi_endpoint = url_template.format(address=contract_address)
    abi = json.loads(requests.get(abi_endpoint).text)
    return abi

