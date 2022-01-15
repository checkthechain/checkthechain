import copy

from . import abi_io
from .. import event_utils


#
# # summaries
#


async def async_summarize_contract_abi(
    contract_abi=None, contract_address=None
):
    if contract_abi is None:
        contract_abi = abi_io.async_get_contract_abi(
            contract_address=contract_address,
        )
    df = contract_abi_to_dataframe(contract_abi, human_readable=True)
    import IPython  # type: ignore

    IPython.display.display(df)


def summarize_contract_events(*, contract_abi=None, events=None):

    if events is None:
        events = get_contract_events(contract_abi=contract_abi)

    print(len(events), 'events:')
    for event in events.values():
        print('-', event['name'])
        for var in event['inputs']:
            if var['indexed']:
                index = 'topic'
            else:
                index = 'data'
            print('    - ' + var['name'] + ':', var['type'] + ',', index)


def get_contract_events(contract_abi=None, **abi_query):
    """get contract events by hash, as {event_hash: event_abi}"""

    if contract_abi is None:
        contract_abi = abi_io.get_contract_abi(**abi_query)

    return {
        binary.get_event_hash(event_abi=abi_item): abi_item
        for abi_item in contract_abi
        if abi_item['type'] == 'event'
    }


#
# # dataframes
#


def contract_abi_to_dataframe(contract_abi, human_readable):
    contract_abi = copy.deepcopy(contract_abi)
    for entry in contract_abi:

        if human_readable:

            if 'name' not in entry:
                entry['name'] = ''

            if 'inputs' in entry:
                inputs = []
                for input in entry['inputs']:
                    input_str = ''
                    input_str += input.get('type')
                    input_name = input.get('name')
                    if input_name is not None and input_name != '':
                        input_str += ' ' + input_name
                    inputs.append(input_str)
                entry['inputs'] = ', '.join(inputs)
            else:
                entry['inputs'] = ''

            if 'outputs' in entry:
                outputs = []
                for output in entry['outputs']:
                    output_str = ''
                    output_str += output.get('type')
                    output_name = output.get('name')
                    if output_name is not None and output_name != '':
                        output_str += ' ' + output_name
                    outputs.append(output_str)
                entry['outputs'] = ', '.join(outputs)
            else:
                entry['outputs'] = ''

            if 'anonymous' not in entry:
                entry['anonymous'] = ''

            if 'stateMutability' not in entry:
                entry['stateMutability'] = ''

    import pandas as pd

    df = pd.DataFrame(contract_abi)
    df = df.reindex(
        columns=[
            'type',
            'name',
            'inputs',
            'outputs',
            'stateMutability',
            'anonymous',
        ]
    )

    return df


def get_contract_events_dataframe(
    contract_abi, contract_name=None, contract_address=None, protocol_name=None
):
    event_abis = event_utils.async_get_contract_events(
        contract_abi=contract_abi
    )
    event_rows = []
    for event_hash, event_abi in event_abis.items():

        data_types = binary.get_event_data_types(event_abi=event_abi)
        data_names = binary.get_event_data_names(event_abi=event_abi)
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

    import pandas as pd

    return pd.DataFrame(event_rows)

