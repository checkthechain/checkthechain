import json

from ctc import spec
from .... import address_utils


# temporary ratelimit, use toolratelimit in future
import time

_last_request = {'time': None}


def get_contract_abi_from_etherscan(contract_address):
    """fetch contract abi using etherscan"""

    import requests
    print('fetching abi from etherscan:', contract_address)

    # ratelimit
    cadence = 6
    current_time = time.time()
    if (
        _last_request['time'] is not None
        and current_time < _last_request['time'] + cadence
    ):
        sleep_time = _last_request['time'] + cadence - current_time
        sleep_time = max(0, sleep_time)
        print('sleeping', sleep_time, 'seconds for etherscan ratelimit')
        time.sleep(sleep_time)
    _last_request['time'] = time.time()

    if not address_utils.is_address_str(contract_address):
        raise Exception('not a valid address: ' + str(contract_address))
    url_template = 'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw'
    abi_endpoint = url_template.format(address=contract_address)
    content = requests.get(abi_endpoint).text
    if content == 'Contract source code not verified':
        raise spec.AbiNotFoundException()
    abi = json.loads(content)
    if isinstance(abi, dict) and abi.get('status') == '0':
        raise Exception(
            'could not obtain contract abi from etherscan for '
            + str(contract_address)
        )
    return abi

