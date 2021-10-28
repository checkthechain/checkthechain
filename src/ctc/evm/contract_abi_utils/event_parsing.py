from .. import binary_utils
from . import contract_abi_io
from . import function_parsing


#
# # querying for events
#


def get_event_abi(
    *,
    contract_address=None,
    contract_abi=None,
    event_name=None,
    event_hash=None,
):
    """get event abi from contract abi"""

    # get contract abi
    if contract_abi is None:
        contract_abi = contract_abi_io.get_contract_abi(
            contract_address=contract_address,
        )

    if event_name is None and event_hash is None:
        raise Exception('specify event_name or event_hash')

    candidates = []
    for item in contract_abi:
        if item['type'] != 'event':
            continue
        if event_name is not None and item.get('name') != event_name:
            continue
        if event_hash is not None:
            item_hash = get_event_hash(
                event_abi=item, contract_abi=contract_abi
            )
            if item_hash != event_hash:
                continue

        candidates.append(item)

    if len(candidates) == 0:
        raise Exception('could not find event abi')
    elif len(candidates) == 1:
        return candidates[0]
    else:
        raise Exception('found too many candidates for event abi')


#
# # parsing event properties
#


def get_event_hash(*, output_format='prefix_hex', **abi_query):
    """compute event hash from event's abi"""
    signature = get_event_signature(**abi_query)
    return binary_utils.keccak_text(signature, output_format=output_format)


def get_event_signature(event_abi=None, **abi_query):
    if event_abi is None:
        event_abi = get_event_abi(**abi_query)
    arg_types = [var['type'] for var in event_abi['inputs']]
    arg_types = [
        function_parsing.get_function_selector_type(item) for item in arg_types
    ]
    inputs = ','.join(arg_types)
    return event_abi['name'] + '(' + inputs + ')'


def get_event_unindexed_types(*, event_abi=None, **abi_query):
    """get list of data types in signature of event"""
    if event_abi is None:
        event_abi = get_event_abi(**abi_query)
    return [var['type'] for var in event_abi['inputs'] if not var['indexed']]


def get_event_unindexed_names(*, event_abi=None, **abi_query):
    """get list of data names in signature of event"""
    if event_abi is None:
        event_abi = get_event_abi(**abi_query)
    return [var['name'] for var in event_abi['inputs'] if not var['indexed']]


def get_event_indexed_names(*, event_abi=None, **abi_query):
    """get list of indexed names in signature of event"""
    if event_abi is None:
        event_abi = get_event_abi(**abi_query)
    return [var['name'] for var in event_abi['inputs'] if var['indexed']]


def get_event_indexed_types(*, event_abi=None, **abi_query):
    """get list of indexed types in signature of event"""
    if event_abi is None:
        event_abi = get_event_abi(**abi_query)
    return [var['type'] for var in event_abi['inputs'] if var['indexed']]

