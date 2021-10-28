import sha3

from .. import binary_utils
from . import contract_abi_io


#
# # querying for functions
#


def get_function_abi(
    function_name=None,
    contract_abi=None,
    contract_address=None,
    n_parameters=None,
    parameter_types=None,
    function_selector=None,
):
    if contract_abi is None:
        contract_abi = contract_abi_io.get_contract_abi(
            contract_address=contract_address
        )

    candidates = []
    for item in contract_abi:
        if item.get('type') != 'function':
            continue
        if function_name is not None and item.get('name') != function_name:
            continue
        if n_parameters is not None and len(item['inputs']) != n_parameters:
            continue
        if parameter_types is not None:
            item_parameter_types = (
                subitem['type'] for subitem in item['inputs']
            )
            if parameter_types != item_parameter_types:
                continue
        if function_selector is not None:
            item_selector = get_function_selector(function_abi=item)
            item_selector = binary_utils.match_binary_format(
                format_this=item_selector,
                like_this=function_selector,
            )
            if item_selector != function_selector:
                continue
        candidates.append(item)

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise Exception('could not find function abi')
    elif len(candidates) > 0:
        raise Exception('too many candidates found for function abi')
    else:
        raise Exception('internal error')


#
# # parsing function properties
#


def get_function_parameter_types(
    function_abi=None, function_signature=None, **abi_query
):
    if function_signature is not None:
        parameter_str = function_signature.split('(')[1]
        parameter_str = parameter_str[:-1]
        return parameter_str.split(',')

    if function_abi is None:
        function_abi = get_function_abi(**abi_query)
    parameter_types = [item['type'] for item in function_abi.get('inputs')]
    return parameter_types


def get_function_parameter_names(function_abi=None, **abi_query):
    if function_abi is None:
        function_abi = get_function_abi(**abi_query)
    parameter_types = [item.get('name') for item in function_abi.get('inputs')]
    return parameter_types


def get_function_signature(
    *, parameter_types=None, function_name=None, function_abi=None, **abi_query
):
    """
    Valid Input Sets:
    - {function_abi}
    - {function_name, parameter_types}
    - {function_name, contract_abi}
    """

    if parameter_types is None:
        parameter_types = get_function_parameter_types(
            function_abi=function_abi, function_name=function_name, **abi_query
        )

    parameter_types = [
        get_function_selector_type(item)
        for item in parameter_types
    ]

    if function_name is None:
        function_name = function_abi['name']

    return function_name + '(' + ','.join(parameter_types) + ')'


def get_function_selector_type(datatype):
    """get the data name used for function selector"""
    if datatype == 'uint':
        return 'uint256'
    elif datatype == 'int':
        return 'int256'
    elif datatype == 'ufixed':
        return 'ufixed128x18'
    elif datatype == 'fixed':
        return 'fixed128x18'
    else:
        return datatype


def get_function_selector(
    *, output_format=None, function_signature=None, **abi_query
):

    if function_signature is None:
        function_signature = get_function_signature(**abi_query)

    full_hash = sha3.keccak_256(function_signature.encode())
    head_bytes = full_hash.hexdigest()[:8]
    return binary_utils.convert_binary_format(head_bytes, output_format)


def get_function_output_types(*, function_abi=None, **abi_query):
    if function_abi is None:
        function_abi = get_function_abi(**abi_query)
    return [output['type'] for output in function_abi['outputs']]

