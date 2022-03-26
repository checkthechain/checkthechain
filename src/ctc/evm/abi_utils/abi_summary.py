import copy

from ctc import binary
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


def print_contract_abi_human_readable(
    contract_abi, max_width=80, verbose=False,
):
    df = contract_abi_to_dataframe(
        contract_abi=contract_abi, human_readable=False
    )

    functions = df[df['type'] == 'function']
    functions = functions.drop(columns=['type', 'anonymous'])

    print('Contract ABI Functions')
    print('──────────────────────')
    for i, (f, function) in enumerate(functions.iterrows()):

        if len(function['outputs']) == 0:
            output_str = '[none]'
        else:
            output_str_list = [
                item['type'] + ' ' + item['name']
                for item in function['outputs']
            ]
            output_str = ', '.join(output_str_list)
            if len(function['outputs']) > 1:
                output_str = '(' + output_str + ')'

        if not verbose:
            signature = binary.get_function_signature(
                function_abi=function, include_names=True
            )
        else:
            signature = function['name'] + '()'
        if verbose:
            text = signature + ' --> ' + str(output_str)
        else:
            text = str(i + 1) + '. ' + signature + ' --> ' + str(output_str)

        if len(text) > max_width:
            text = text[: max_width - 3] + '...'

        print(text)
        if verbose:
            indent = ''
            if verbose > 1:
                indent = '    '
                print(indent + '- mutability:', function['stateMutability'])
                print(indent + '- inputs:')
            if len(function['inputs']) == 0:
                print(indent + '    [no inputs]')
            for i, item in enumerate(function['inputs']):
                print(
                    indent + '    ' + str(i + 1) + '.',
                    item['type'],
                    item['name'],
                )
            print()

    events = df[df['type'] == 'event']
    print()
    print('Contract ABI Events')
    print('───────────────────')
    if len(events) == 0:
        print('[none]')
    for i, (e, event) in enumerate(events.iterrows()):
        event_hash = binary.get_event_hash(event_abi=event)
        signature = binary.get_event_signature(event_abi=event)
        line = str(i + 1) + '. ' + signature
        if len(line) > max_width:
            line = line[: max_width - 3] + '...'
        print(line)
        if verbose:
            print('  ', event_hash)
            if i + 1 != len(events):
                print()


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

