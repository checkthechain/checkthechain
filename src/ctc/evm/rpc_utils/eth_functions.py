import json

import requests

from ctc import config_utils
from .. import contract_abi_utils


def eth_call(
    contract_address,
    provider=None,
    call_data=None,
    parameters=None,
    decode_result=True,
    delist_single_outputs=True,
    **function_abi_query
):

    # encode call data
    if call_data is None:
        call_data = contract_abi_utils.encode_call_data(
            parameters=parameters,
            contract_address=contract_address,
            **function_abi_query
        )

    # assemble request data
    parameters = {
        'to': contract_address,
        'data': call_data,
    }
    data = {
        'jsonrpc': '2.0',
        'method': 'eth_call',
        'params': [parameters],
        'id': 1,
    }

    # perform request
    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']
    response = requests.post(url=provider, data=json.dumps(data))

    # process response
    response_data = response.json()
    result = response_data['result']
    if decode_result:
        result = contract_abi_utils.decode_function_output(
            encoded_output=result,
            contract_address=contract_address,
            delist_single_outputs=delist_single_outputs,
            **function_abi_query
        )

    return result

