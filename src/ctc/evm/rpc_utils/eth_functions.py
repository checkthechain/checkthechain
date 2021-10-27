import json

import requests
import web3

from ctc import config_utils


def eth_call(contract_address, provider=None, **kwargs):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    parameters = {
        'to': contract_address,
    }
    parameters.update(kwargs)

    data = {
        'jsonrpc': '2.0',
        'method': 'eth_call',
        'params': [parameters],
        'id': 1234,
    }
    data = json.dumps(data)

    response = requests.post(url=provider, data=data)
    response_data = response.json()
    return response_data['result']


def eth_event_filter(contract_address=None, topics=None, start_block=None, end_block=None):
    if start_block is not None:
#         start_block = hex(start_block)
        start_block = web3.Web3(endpoint).toHex(start_block)
    if end_block is not None:
        end_block = web3.Web3(endpoint).toHex(end_block)
#         end_block = hex(end_block)

    parameters = {
        'address': contract_address,
        'topics': topics,
        'fromBlock': start_block,
        'toBlock': end_block,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    data = {
        'jsonrpc': '2.0',
        'method': 'eth_newFilter',
        'params': [parameters],
        'id': 1234,
    }
    data = json.dumps(data)

    response = requests.post(url=endpoint, data=data)
    response_data = response.json()
    return response_data['result']


def eth_get_filter_changes(filter_id):
    data = {
        'jsonrpc': '2.0',
        'method': 'eth_getFilterChanges',
        'params': [filter_id],
        'id': 1234,
    }
    data = json.dumps(data)

    response = requests.post(url=endpoint, data=data)
    response_data = response.json()
    print(response_data)
    return response_data['result']


def eth_get_filter_logs(filter_id):
    data = {
        'jsonrpc': '2.0',
        'method': 'eth_getFilterLogs',
        'params': [filter_id],
        'id': 1234,
    }
    data = json.dumps(data)

    response = requests.post(url=endpoint, data=data)
    response_data = response.json()
    return response_data['result']

