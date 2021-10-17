import pandas as pd

from . import event_querying


def summarize_contract_events(*, contract_abi=None, events=None):

    if events is None:
        events = event_querying.get_contract_events(contract_abi=contract_abi)

    print(len(events), 'events:')
    for event in events.values():
        print('-', event['name'])
        for var in event['inputs']:
            if var['indexed']:
                index = 'topic'
            else:
                index = 'data'
            print('    - ' + var['name'] + ':', var['type'] + ',', index)


def get_contract_events_dataframe(
    contract_abi, contract_name=None, contract_address=None, protocol_name=None
):
    event_abis = event_querying.get_contract_events(contract_abi=contract_abi)
    event_rows = []
    for event_hash, event_abi in event_abis.items():

        data_types = event_querying.get_event_data_types(event_abi=event_abi)
        data_names = event_querying.get_event_data_names(event_abi=event_abi)
        data_signature = [
            data_type + ' ' + data_name
            for data_type, data_name in zip(data_types, data_names)
        ]

        event_row = {
            'protocol_name': protocol_name,
            'contract_address': contract_address,
            'contract_name': contract_name,
            'event_name': event_abi['name'],
            'event_hash': event_hash,
            'topic1_type': None,
            'topic1_name': None,
            'topic2_type': None,
            'topic2_name': None,
            'topic3_type': None,
            'topic3_name': None,
            'data_signature': data_signature,
        }

        n_topics = 0
        for var in event_abi['inputs']:
            if var['indexed']:
                n_topics += 1
                event_row['topic' + str(n_topics) + '_type'] = var['type']
                event_row['topic' + str(n_topics) + '_name'] = var['name']

        event_rows.append(event_row)

    return pd.DataFrame(event_rows)

