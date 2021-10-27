
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


