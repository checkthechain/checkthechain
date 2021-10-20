import json

import requests

from ... import address_utils


def get_contract_abi_from_etherscan(contract_address):
    """fetch contract abi using etherscan"""
    if not address_utils.is_address_str(contract_address):
        raise Exception('not a valid address: ' + str(contract_address))
    url_template = 'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw'
    abi_endpoint = url_template.format(address=contract_address)
    abi = json.loads(requests.get(abi_endpoint).text)
    if isinstance(abi, dict) and abi.get('status') == '0':
        raise Exception('could not obtain contract abi from etherscan for ' + str(contract_address))
    return abi

