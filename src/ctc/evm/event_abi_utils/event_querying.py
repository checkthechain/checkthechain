import web3

from .. import contract_abi_utils
from . import event_decoding


#
# # querying within a contract abi
#

def get_contract_events(*, contract=None, contract_abi=None):
    """get contract events by hash, as {event_hash: event_abi}"""

    if isinstance(contract, web3.eth.Contract):
        abi_items = contract.abi
    elif isinstance(contract, list):
        abi_items = contract
    elif isinstance(contract_abi, list):
        abi_items = contract_abi
    else:
        raise Exception('unknown contract format')

    return {
        get_event_hash(event_abi=abi_item): abi_item
        for abi_item in abi_items
        if abi_item['type'] == 'event'
    }


def get_event_hash(event_abi):
    """compute event hash from event's abi"""
    inputs = ','.join(var['type'] for var in event_abi['inputs'])
    event_signature_text = event_abi['name'] + '(' + inputs + ')'
    event_hash = web3.Web3.sha3(text=event_signature_text).hex()
    return event_hash


def get_event_abi(
    *,
    contract_address=None,
    contract_abi=None,
    event_name=None,
    event_hash=None,
    contract_name=None,
    protocol=None
):
    """get event abi from contract abi"""

    if contract_abi is None:
        if contract_name is not None:
            contract_abi = contract_abi_utils.load_abi_by_name(
                contract_name=contract_name, project=protocol
            )
        elif contract_address is not None:
            contract_abi = contract_abi_utils.get_contract_abi(
                contract_address=contract_address,
            )
        else:
            raise Exception('could not find contract_abi')

    for event_abi in contract_abi:

        if event_abi['type'] == 'event':

            if event_name is not None:
                if event_abi['name'] == event_name:
                    return event_abi
            elif event_hash is not None:
                if get_event_hash(event_abi) == event_hash:
                    return event_abi
            else:
                raise Exception('specify event_name or event_hash')

    else:
        raise Exception('could not find event abi')


#
# # querying within an event abi
#


def get_event_data_types(*, event_abi=None, event_hash=None, contract_abi=None):
    """get list of data types in signature of event"""
    if event_abi is None:
        kwargs = dict(event_hash=event_hash, contract_abi=contract_abi)
        event_abi = get_event_abi(**kwargs)
    return [var['type'] for var in event_abi['inputs'] if not var['indexed']]


def get_event_data_names(*, event_abi=None, event_hash=None, contract_abi=None):
    """get list of data names in signature of event"""
    if event_abi is None:
        kwargs = dict(event_hash=event_hash, contract_abi=contract_abi)
        event_abi = get_event_abi(**kwargs)
    return [var['name'] for var in event_abi['inputs'] if not var['indexed']]


def get_event_indexed_names(
    *, event_abi=None, event_hash=None, contract_abi=None
):
    """get list of indexed names in signature of event"""
    if event_abi is None:
        kwargs = dict(event_hash=event_hash, contract_abi=contract_abi)
        event_abi = get_event_abi(**kwargs)
    return [var['name'] for var in event_abi['inputs'] if var['indexed']]


def get_event_indexed_types(
    *, event_abi=None, event_hash=None, contract_abi=None
):
    """get list of indexed types in signature of event"""
    if event_abi is None:
        kwargs = dict(event_hash=event_hash, contract_abi=contract_abi)
        event_abi = get_event_abi(**kwargs)
    return [var['type'] for var in event_abi['inputs'] if var['indexed']]


#
# # top level querying
#

def filter_events(
    raw_events,
    event_name=None,
    event_hash=None,
    contract_name=None,
    contract_abi=None,
    protocol=None,
    decode=True,
    contract_address=None,
):
    event_abi = get_event_abi(
        event_name=event_name,
        event_hash=event_hash,
        protocol=protocol,
        contract_name=contract_name,
        contract_abi=contract_abi,
    )
    event_hash = get_event_hash(event_abi=event_abi)
    filtered_events = raw_events[raw_events['topic0'] == event_hash]

    if contract_address is not None:
        filtered_events = filtered_events[
            filtered_events['contract_address'] == contract_address
        ]

    if decode:
        filtered_events = event_decoding.decode_events(
            df=filtered_events,
            event_abi=event_abi,
        )

    return filtered_events


def filter_events_by_type(logs, contract_address=None):

    events_by_name = {}
    events_by_hash = {}

    if len(logs) > 1:

        if contract_address is not None:
            logs = logs[logs['contract_address'] == contract_address]
        else:
            assert len(set(logs['contract_address'])) == 1
            contract_address = logs['contract_address'].values[0]

        contract_abi = contract_abi_utils.load_named_abi_by_address(
            contract_address=contract_address
        )

        event_hashes = set(logs['topic0'].values)
        for event_hash in event_hashes:
            type_events = filter_events(
                event_hash=event_hash,
                contract_abi=contract_abi,
                contract_address=contract_address,
                raw_events=logs,
            )
            event_abi = get_event_abi(
                contract_abi=contract_abi,
                event_hash=event_hash,
            )
            events_by_hash[event_hash] = type_events
            events_by_name[event_abi['name']] = type_events

    return {
        'events_by_hash': events_by_hash,
        'events_by_name': events_by_name,
    }


