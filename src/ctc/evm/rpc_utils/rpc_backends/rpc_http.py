import json

import requests


def rpc_call_http(method, parameters, provider=None, decode_result=True):

    # assemble payload
    data = {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': 1,
    }

    # perform request
    response = requests.post(url=provider, data=json.dumps(data))
    response_data = response.json()
    result = response_data['result']

    return result

